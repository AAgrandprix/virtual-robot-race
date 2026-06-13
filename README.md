# aira — Virtual Robot Race

**Race your Algorithm. Challenge the World.**

![aira — Virtual Robot Race](scripts/hero.gif)

The official simulator for **[aira](https://aira-race.com)** — Autonomous Intelligence Racing Arena.
Train your AI algorithm, race against others, and climb the global leaderboard.

> **Platform**: Windows only (Mac/Linux support planned).

---

## Requirements

| | |
|---|---|
| **OS** | Windows 10 / 11 (64-bit) |
| **Python** | 3.10 – 3.12 |
| **GPU** | A dedicated GPU is **strongly recommended** for AI mode. The simulator runs in real time, so the control loop must keep up with the camera (target **20 fps**). |
| **Environment** | Run on a **physical local PC**. Remote VMs / cloud instances / RDP sessions are **not recommended** (see below). |

> **⚠ Why machine speed matters:** the race world advances in real time and does **not** wait for a slow client. On an underpowered machine (no GPU, or a remote VM), the control loop can drop to a few updates per second — too slow to steer the sample algorithm reliably, so the robot crashes or falls off the track and **no time is recorded**. `main.py` now reports your effective camera rate at the end of each run and warns if it is below 8 fps.

> **⚠ Account sign-in:** create your aira account and sign in from a **browser on your local PC**. Google sign-in is often blocked from datacenter / VM / RDP IP addresses, which can make account creation fail.

---

## Getting Started

New to aira? The tutorial on the platform walks you through everything — Fork, Setup, and your first race — with video guides.

→ **[aira-race.com/getting-started](https://aira-race.com/getting-started)**

---

## Quick Start

For developers who want to get running immediately:

```bash
# 1. Clone
git clone https://github.com/aira-race/virtual-robot-race.git
cd virtual-robot-race

# 2. Setup (or double-click setup_env.bat)
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run (or double-click start.bat)
python main.py
```

Unity launches automatically and the race begins.

---

## Lessons

Step-by-step curriculum — from environment setup to submitting your first competition result.
No prior AI experience required. Available in English and Japanese.

→ **[docs/README.md](docs/README.md)**

---

## Community & Support

| | |
|---|---|
| Platform & Leaderboard | [aira-race.com](https://aira-race.com) |
| Competitions | [aira-race.com/competitions](https://aira-race.com/competitions) |
| YouTube | [@RaceYourAlgo](https://www.youtube.com/@aira_race) |
| X (Twitter) | [@RaceYourAlgo](https://x.com/aira_race) |
| Issues | [GitHub Issues](https://github.com/aira-race/virtual-robot-race/issues) |

---

## Version History

### Version 1.7.1 (2026-06-13)
- **New**: End-of-race result feedback — `main.py` now states clearly whether your time was recorded (`✓ RESULT RECORDED`), was not counted (invalid run: fell off track / false start / battery depleted / laps not completed), or was skipped because Race Flag was `TEST ONLY`
- **New**: Effective camera-rate report and low-performance warning (warns below 8 fps; design target is 20 fps)
- **New**: Requirements & troubleshooting guidance (GPU recommended, local PC over remote VM, local-browser account sign-in)
- *(Client-side only; Unity executable remains `aira_Beta_1.7.exe`.)*

### Version 1.7 (2026-03-15)
- **New**: aira HUD redesign — status panel (PLAYER / COMP / MODE / LAP / SOC / STATUS), race timer, camera view with SOC bar
- **New**: GAS (Google Apps Script) backend v2 — tutorial and competition result posting
- **New**: Competition mode — player verification before race start
- **Change**: Unified config — all settings in a single `config.txt`
- **Change**: `COMPETITION_NAME` replaces `COMP_NAME`; default is `Tutorial`
- **Change**: `NAME` accepts underscores (`_`), up to 16 characters
- **Change**: Only the fastest result per race is submitted
- **Rebrand**: Executable renamed to `aira_Beta_1.7.exe`

### Version 1.6 (2026-02-28)
- **New**: Tail lamp controller with shader — hue reflects steering, brightness reflects throttle

### Version 1.5 (2026-02-08)
- **New**: Collision penalty system — collisions drain battery (SOC) proportional to impact energy
- **New**: Collision data logged per-frame in metadata.csv
- **New**: Battery depletion status — depleted robots become obstacles on track

### Version 1.4 (2026-01-17)
- **New**: Offline RL training pipeline (DAgger+, AWR)

### Version 1.3 (2026-01-11)
- **New**: Smartphone controller mode (MODE_NUM=5)
- **New**: PanelManager for dynamic camera panel layout

### Version 1.2 (2026-01-10)
- **Fix**: Training data image/metadata alignment (328-frame offset resolved)

### Version 1.1 (2025-12-13)
- **New**: Real-time Input Vector Scope visualization
- **New**: Rule-Based autonomous driving achieves 2-lap goal
