# main.py
# Entry point for launching Unity + control system via WebSocket and input mode

import asyncio
import threading
import subprocess
import os
import keyboard

import config
import websocket_server
import keyboard_input
import inference_input
import table_input  # Required for table mode

stop_event = threading.Event()  # Global event to signal thread stop

def launch_unity_exe():
    """Launch the Unity .exe if it exists."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(base_dir, "Windows", "AAgp_test30.exe")

    if os.path.exists(exe_path):
        print(f"[Main] Launching Unity app: {exe_path}")
        subprocess.Popen([exe_path], shell=True)
    else:
        print(f"[Main] Unity .exe not found at: {exe_path}")

async def main():
    print("[Main] Starting system...")
    race_end_sent = False

    # Start WebSocket server
    server_task = asyncio.create_task(websocket_server.start_server(stop_event))

    # Launch Unity only if not in DEBUG mode
    if config.DEBUG_MODE == 0:
        launch_unity_exe()
    else:
        print("[Main] DEBUG_MODE = 1 → Please launch Unity manually.")

    input_thread = None

    if config.MODE == "keyboard":
        input_thread = threading.Thread(target=keyboard_input.listen_for_input, args=(stop_event,), daemon=True)
        input_thread.start()

    elif config.MODE == "ai":
        await asyncio.to_thread(websocket_server.frame_received_event.wait)
        input_thread = threading.Thread(target=inference_input.run_ai_loop, args=(stop_event,), daemon=True)
        input_thread.start()

    elif config.MODE == "rule_based":
        await asyncio.to_thread(websocket_server.frame_received_event.wait)
        import rule_based_input  # Lazy import
        input_thread = threading.Thread(target=rule_based_input.run_rule_based_loop, args=(stop_event,), daemon=True)
        input_thread.start()

    elif config.MODE == "table":
        await asyncio.to_thread(websocket_server.frame_received_event.wait)
        table_input.start_csv_replay()
        input_task = asyncio.create_task(table_input.run_table_input_loop(stop_event))

    try:
        while not stop_event.is_set():
            await asyncio.sleep(0.1)

            if keyboard.is_pressed("q") and not race_end_sent:
                print("[Main] 'q' pressed → Forcing race end.")
                await websocket_server.send_race_end_signal()
                race_end_sent = True

    except KeyboardInterrupt:
        print("[Main] KeyboardInterrupt received. Exiting...")
        stop_event.set()

    # Cleanup
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        print("[Main] Server task cancelled.")

    stop_event.set()
    if input_thread:
        input_thread.join()

    print("[Main] System fully stopped.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()
        print("[Main] Program exited.")
