# Project Alpha – Virtual Robot Race

This is the **Alpha version** of the Virtual Robot Race project.  
You can manually drive the robot, replay pre-recorded torque data, or try rule-based and AI-controlled driving.

---

## 🚀 How to Use

1. Clone this repository
2. Install Python 3.10+
3. Install required packages:

pip install -r requirements.txt

4. Run the Python main script:

python main.py

6. Set the control mode in `config.txt`:
- `1 = keyboard`
- `2 = table (CSV)`
- `3 = rule_based`
- `4 = ai (requires model.pth)`

---

## 🧠 AI Model Download

The AI mode requires a trained model file `model.pth`.

> ⚠️ This file is **not included** in the repository due to GitHub’s 100MB limit.

👉 [Download model.pth from Google Drive] https://drive.google.com/file/d/19qWtxAC1ABYiK1CGDg9A0PDX67u39I_v/view?usp=sharing


After downloading, place the file in this path:

Project_Alpha/models/model.pth



Make sure the filename is exactly `model.pth`.

---

## 🗂 Folder Structure

```
project/
├── main.py
├── websocket_server.py
├── config.py
├── config.txt
├── keyboard_input.py
├── table_input.py
├── table_input.csv
├── data_interactive/
├── rule_based_input.py
├── rule_based_algorithms/
│   ├── perception_Startsignal.py
│   ├── Linetrace_white.py
│   └── status_Robot.py
├── inference_input.py
├── models/
│   └── model.pth   <dowonload from google drive>
├── data_manager.py
├── Windows/
│   ├── AAgp_test30.exe
│   ├── runtime_log.txt
│   ├── UnityCrashHandler64.exe
│   ├── UnityPlayer.dll
│   ├── AAgp_test30_Data/
│   └── MonoBleedingEdge/
└── training_data/
│   └──run_YYYYMMDD_HHMMSS/
│       └──images/
│           ├── frame_00001.jpg
│           ├── frame_00002.jpg
│           └── ...
│       └──metadata.csv
│       └──table_input.csv
│       └──UnityLog.txt   
```

---

## 💡 Notes

- Training data is saved in `/training_data/` when enabled.
- Logs and debug images are saved per run.
- This is a work-in-progress Alpha version and may contain bugs or changes in the future.

---

Race your algorithm! 🏁

