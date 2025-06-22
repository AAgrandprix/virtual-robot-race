# websocket_server.py
# WebSocket server to communicate with Unity, send torque and receive sensor/image data

import asyncio
import websockets
import os
import json
import config
import keyboard_input  # For keyboard mode
from data_manager import save_image_and_soc, save_race_metadata, copy_unity_log_to_run_dir
from table_input import start_csv_replay
from threading import Event

frame_received_event = Event()  # Trigger when first JPEG arrives
TORQUE_FILE = os.path.join("data_interactive", "latest_torque.txt")

first_frame_received = False
shutdown_event = asyncio.Event()
connected_websocket = None

# Select appropriate control module based on mode
if config.MODE == "keyboard":
    import keyboard_input as control_module
elif config.MODE == "table":
    import table_input as control_module
elif config.MODE == "rule_based":
    import rule_based_input as control_module
elif config.MODE == "ai":
    import inference_input as control_module
else:
    raise ValueError(f"[Server] Unknown control mode: {config.MODE}")

async def send_torque_data(websocket):
    """Send torque command to Unity every 50ms"""
    print("[Server] Starting torque data sender...")
    while not shutdown_event.is_set():
        await asyncio.sleep(0.05)
        message = json.dumps({
            "type": "control",
            "leftTorque": control_module.leftTorque,
            "rightTorque": control_module.rightTorque
        })
        try:
            write_latest_torque(control_module.leftTorque, control_module.rightTorque)
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("[Server] WebSocket closed. Stopping torque sender.")
            break

async def receive_image_and_soc(websocket):
    """Receive JPEG + SOC + metadata from Unity"""
    global first_frame_received
    print("[Server] Ready to receive data from Unity...")

    try:
        async for message in websocket:
            if isinstance(message, (bytes, bytearray)):
                filename = save_image_and_soc(message)
                if filename == "frame_000001.jpg" and not first_frame_received:
                    first_frame_received = True
                    frame_received_event.set()
                    print("[Server] First frame received.")
            else:
                try:
                    race_data = json.loads(message)
                    print("[Server] Received race metadata.")
                    save_race_metadata(race_data)
                except json.JSONDecodeError as e:
                    print(f"[Server] JSON decode error: {e}")

    except websockets.exceptions.ConnectionClosed:
        print("[Server] Client disconnected.")
    finally:
        print("[Server] Image/SOC reception stopped.")

async def handler(websocket, stop_event):
    """Handle new client connection"""
    global connected_websocket
    connected_websocket = websocket
    print("[Server] Client connected.")

    try:
        await websocket.send(json.dumps({"type": "connection", "status": "success"}))
        print("[Server] Sent handshake to Unity.")
    except websockets.exceptions.ConnectionClosed:
        print("[Server] Connection failed during handshake.")
        return

    send_task = asyncio.create_task(send_torque_data(websocket))
    receive_task = asyncio.create_task(receive_image_and_soc(websocket))

    try:
        await receive_task
    finally:
        print("[Server] Connection closed.")
        shutdown_event.set()
        stop_event.set()
        send_task.cancel()
        receive_task.cancel()

async def send_race_end_signal():
    """Send race end command to Unity"""
    if connected_websocket:
        try:
            message = json.dumps({"type": "connection", "message": "RaceEnd"})
            await connected_websocket.send(message)
            print("[Server] Sent RaceEnd signal to Unity.")
        except Exception as e:
            print(f"[Server] Failed to send RaceEnd: {e}")
    else:
        print("[Server] No client connected to send RaceEnd.")

async def start_server(stop_event):
    """Launch WebSocket server and wait for client"""
    server = await websockets.serve(lambda ws: handler(ws, stop_event), config.HOST, config.PORT)
    print(f"[Server] WebSocket server running at ws://{config.HOST}:{config.PORT}")
    await shutdown_event.wait()

    print("[Server] Shutting down server...")
    server.close()
    await server.wait_closed()
    stop_event.set()

async def send_control_command_async(left, right):
    """Send manual torque control via WebSocket (used in table mode)"""
    if connected_websocket:
        try:
            message = json.dumps({
                "type": "control",
                "leftTorque": left,
                "rightTorque": right
            })
            await connected_websocket.send(message)
            print(f"[Server] Sent manual torque: L={left}, R={right}")
        except Exception as e:
            print(f"[Server] Error sending torque: {e}")
    else:
        print("[Server] No connected client.")

def write_latest_torque(left, right):
    try:
        with open(TORQUE_FILE, "w") as f:
            f.write(f"{left:.4f},{right:.4f}")
    except Exception as e:
        print(f"[Server] Failed to write torque to file: {e}")
