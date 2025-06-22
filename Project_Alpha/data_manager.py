# data_manager.py
# Handles image + SOC saving, metadata logging, and folder management

import os
import time
import json
import struct
import csv
import shutil
import config
import tempfile
import sys

# === Base Directory Handling ===
if getattr(sys, 'frozen', False):
    # In case of PyInstaller build
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Directory structure ===
INTERACTIVE_DIR = os.path.join(BASE_DIR, "data_interactive")
os.makedirs(INTERACTIVE_DIR, exist_ok=True)

SOC_FILE = os.path.join(INTERACTIVE_DIR, "latest_SOC.txt")
RGB_FILE_A = os.path.join(INTERACTIVE_DIR, "latest_RGB_a.jpg")
RGB_FILE_B = os.path.join(INTERACTIVE_DIR, "latest_RGB_b.jpg")
RGB_NOW_FILE = os.path.join(INTERACTIVE_DIR, "latest_RGB_now.txt")

# === SOC IO ===
def get_latest_soc():
    try:
        with open(SOC_FILE, "r") as f:
            return float(f.read().strip())
    except Exception:
        return 0.0

def update_latest_soc(soc):
    try:
        with open(SOC_FILE, "w") as f:
            f.write(f"{soc:.4f}")
    except Exception as e:
        print(f"[DataManager] Failed to write SOC: {e}")

# === Create run directory for each session ===
def create_run_directory():
    timestamp = time.strftime("run_%Y%m%d_%H%M%S")
    training_data_dir = os.path.join(BASE_DIR, "training_data")
    os.makedirs(training_data_dir, exist_ok=True)

    run_dir = os.path.join(training_data_dir, timestamp)
    images_dir = os.path.join(run_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    return run_dir, images_dir

run_dir, images_dir = create_run_directory()
_latest_toggle = True

# === Safe JPEG file replace ===
def safe_replace_jpg(tmp_path, target_path):
    for _ in range(10):
        try:
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(tmp_path, target_path)
            break
        except PermissionError:
            time.sleep(0.02)
    else:
        print(f"[DataManager] Failed to replace JPEG after retries: {target_path}")

# === Main data saving logic ===
def save_image_and_soc(data):
    global _latest_toggle
    filename = None

    # Extract header
    json_size = struct.unpack("I", data[:4])[0]
    json_header = data[4:4 + json_size].decode("utf-8")

    try:
        json_obj = json.loads(json_header)
        soc_value = json_obj.get("soc", None)
        filename = json_obj.get("filename", None)
    except json.JSONDecodeError:
        print("[DataManager] Failed to decode JSON header")
        return None

    jpeg_data = data[4 + json_size:]
    if not jpeg_data or len(jpeg_data) < 1000:
        return None

    # Save to training folder
    if filename:
        filename_path = os.path.join(images_dir, filename)
    else:
        filename_path = os.path.join(images_dir, f"frame_{int(time.time() * 1000)}.jpg")

    try:
        with open(filename_path, "wb") as f:
            f.write(jpeg_data)
    except Exception as e:
        print(f"[DataManager] Failed to write training image: {e}")

    # Save to intermediate folder with A/B buffering
    try:
        rgb_file_target = RGB_FILE_A if _latest_toggle else RGB_FILE_B
        tmp_path = rgb_file_target + ".tmp"

        with open(tmp_path, "wb") as f:
            f.write(jpeg_data)

        safe_replace_jpg(tmp_path, rgb_file_target)

        with open(RGB_NOW_FILE, "w") as f:
            f.write("a" if _latest_toggle else "b")

    except Exception as e:
        print(f"[DataManager] Failed to update RGB image: {e}")

    _latest_toggle = not _latest_toggle

    # Save SOC
    if soc_value is not None:
        update_latest_soc(soc_value)

    return os.path.basename(filename_path)

# === Save metadata to CSV ===
def save_race_metadata(race_data):
    metadata_csv_path = os.path.join(run_dir, "metadata.csv")

    if "data" not in race_data:
        print("[DataManager] Invalid metadata: 'data' key missing")
        return

    with open(metadata_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "id", "time_ms", "frame_id", "filename", "soc",
            "wheel_left", "wheel_right", "status",
            "pos_x", "pos_y", "pos_z", "yaw", "error_code"
        ])

        for entry in race_data["data"]:
            writer.writerow([
                entry.get("id"),
                entry.get("time_ms"),
                entry.get("frame_id"),
                entry.get("filename"),
                entry.get("soc"),
                entry.get("wheel_left"),
                entry.get("wheel_right"),
                entry.get("status"),
                entry.get("pos_x"),
                entry.get("pos_y"),
                entry.get("pos_z"),
                entry.get("yaw"),
                entry.get("error_code")
            ])

    print(f"[DataManager] Metadata saved to {metadata_csv_path}")
    copy_unity_log_to_run_dir()
    delete_images_if_flagged()

# === Copy Unity log and table input CSV ===
def copy_unity_log_to_run_dir():
    log_src_path = os.path.join(BASE_DIR, "Windows", "runtime_Log.txt")
    log_dest_path = os.path.join(run_dir, "UnityLog.txt")

    if os.path.exists(log_src_path):
        shutil.copy(log_src_path, log_dest_path)
        print(f"[DataManager] Copied Unity log to {log_dest_path}")

    if config.MODE == "table":
        table_src_path = os.path.join(BASE_DIR, "table_input.csv")
        table_dest_path = os.path.join(run_dir, "table_input.csv")

        if os.path.exists(table_src_path):
            shutil.copy(table_src_path, table_dest_path)
            print(f"[DataManager] Copied table_input.csv to {table_dest_path}")

# === Delete images if config.JPEG_SAVE is 0 ===
def delete_images_if_flagged():
    if config.JPEG_SAVE == 0:
        print("[DataManager] JPEG_SAVE=0 → Deleting all saved JPEGs for lightweight mode")
        for filename in os.listdir(images_dir):
            if filename.endswith(".jpg"):
                try:
                    os.remove(os.path.join(images_dir, filename))
                except Exception as e:
                    print(f"[DataManager] Failed to delete {filename}: {e}")
        print("[DataManager] All JPEG images deleted")
