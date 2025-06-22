# config.py
# Reads and applies configuration values from config.txt

import os

# Default values if config.txt is missing or invalid
DEFAULT_CONFIG = {
    "HOST": "localhost",
    "PORT": 12346,
    "MODE_NUM": 1,         # 1: keyboard, 2: table, 3: rule_based, 4: ai
    "DEBUG_MODE": 0,       # 0: Launch Unity from script, 1: Manually launch Unity
    "JPEG_SAVE": 0         # 1: Save images, 0: Do not save
}

CONFIG_PATH = "config.txt"
CONFIG = DEFAULT_CONFIG.copy()

def load_config():
    """Load key-value pairs from config.txt"""
    if not os.path.exists(CONFIG_PATH):
        print("[Config] config.txt not found. Using default settings.")
        return

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in CONFIG:
                        try:
                            CONFIG[key] = int(value) if value.isdigit() else value
                        except Exception:
                            CONFIG[key] = value
    except Exception as e:
        print(f"[Config] Failed to read config.txt: {e}")

def apply_config():
    """Apply loaded values as global variables"""
    global HOST, PORT, MODE_NUM, MODE, DEBUG_MODE, JPEG_SAVE

    load_config()

    HOST = CONFIG["HOST"]
    PORT = CONFIG["PORT"]
    MODE_NUM = CONFIG["MODE_NUM"]

    MODE_MAP = {
        1: "keyboard",
        2: "table",
        3: "rule_based",
        4: "ai"
    }
    MODE = MODE_MAP.get(MODE_NUM, "keyboard")

    DEBUG_MODE = CONFIG["DEBUG_MODE"]
    JPEG_SAVE = CONFIG["JPEG_SAVE"]

# Initialize settings at import time
apply_config()
