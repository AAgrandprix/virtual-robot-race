# rule_based_input.py
# Entry point script for rule-based control.
# This module loads the latest RGB image and battery status (SOC), evaluates the current control state,
# and delegates image processing to rule-based algorithms for start signal detection and line following.

import time
import os
from PIL import Image
import data_manager

from rule_based_algorithms import status_Robot
from rule_based_algorithms import perception_Startsignal
from rule_based_algorithms import Linetrace_white

leftTorque = 0.0
rightTorque = 0.0

def saturate(value, min_val=-1.0, max_val=1.0):
    """Clamp value between min_val and max_val."""
    return max(min_val, min(max_val, value))

def get_latest_rgb_path():
    """Retrieve the current RGB image path (A/B alternation method)."""
    RGB_NOW_PATH = os.path.join("data_interactive", "latest_RGB_now.txt")
    try:
        with open(RGB_NOW_PATH, "r") as f:
            latest_mark = f.read().strip()
            if latest_mark in ("a", "b"):
                return os.path.join("data_interactive", f"latest_RGB_{latest_mark}.jpg")
    except Exception:
        pass
    return os.path.join("data_interactive", "latest_RGB_a.jpg")  # fallback if missing

def run_rule_based_loop(stop_event):
    """Main control loop for rule-based driving."""
    global leftTorque, rightTorque

    print("[RuleBased] Control loop started.")

    while not stop_event.is_set():
        try:
            # === Retrieve battery State of Charge (SOC)
            soc = data_manager.get_latest_soc()

            # === Load latest RGB image (once per loop)
            image_path = get_latest_rgb_path()
            try:
                img = Image.open(image_path).convert("RGB")
            except Exception as e:
                print(f"[RuleBased] Failed to load image: {e}")
                time.sleep(0.05)
                continue

            # === Get current driving state
            current_state = status_Robot.get_state()

            # --- Waiting for start signal ---
            if current_state == status_Robot.WAITING_START:
                go = perception_Startsignal.detect_start_signal(img)  # pass image object

                if go:
                    status_Robot.set_state(status_Robot.RUN_STRAIGHT)
                else:
                    leftTorque = rightTorque = 0.0
                    time.sleep(0.05)
                    continue

            # --- Straight line following ---
            elif current_state == status_Robot.RUN_STRAIGHT:
                leftTorque, rightTorque = Linetrace_white.run(soc, img)  # pass image object

            # --- All other states (not implemented) ---
            else:
                leftTorque = rightTorque = 0.0

            # Clamp torque values to safe range
            leftTorque = saturate(leftTorque)
            rightTorque = saturate(rightTorque)

            print(f"[RuleBased] Torque: L={leftTorque:.2f}, R={rightTorque:.2f}")

        except Exception as e:
            print(f"[RuleBased] Error: {e}")

        time.sleep(0.05)

    print("[RuleBased] Control loop stopped.")
