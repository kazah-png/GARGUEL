<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1a00,100:2b2b00&height=130&section=header&text=GARGUEL&fontSize=52&fontColor=e6edf3&animation=fadeIn&fontAlignY=55" />
</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-1f6aa5?style=flat)]()
[![pyautogui](https://img.shields.io/badge/pyautogui-automation-3776AB?style=flat)]()
[![License](https://img.shields.io/badge/License-MIT-3fb950?style=flat)](LICENSE)

**Automated click-bot for Steam games with a desktop GUI and SQLite session tracking.**  
Template matching · Configurable difficulty · Hotkeys · Standalone .exe

</div>

---

## Overview

GARGUEL automates repetitive menu navigation in Steam games. It detects on-screen buttons using coordinate-based click sequences calibrated for 1920×1080, advances through difficulty selection and battle mode menus, activates auto mode, waits for the match to complete, and returns to the main menu — all without user interaction.

A CustomTkinter GUI controls the bot, shows live session statistics, and logs every action. Sessions are recorded to a local SQLite database.

---

## Features

| Feature | Details |
|---|---|
| **Automated loop** | Full match cycle in ~50 seconds: start → difficulty → skip intro → auto mode → result → menu |
| **Difficulty selection** | Easy / Normal / Hard — selectable from the GUI before starting |
| **Hotkeys** | Start / Pause / Stop from keyboard without switching windows |
| **GUI** | CustomTkinter interface with session stats, activity log, and status indicator |
| **Session tracking** | SQLite database records timestamp, difficulty, result, and duration per match |
| **Standalone .exe** | PyInstaller build (~25 MB); no Python install required on target machine |

---

## Quick Start

### Option 1 — Python

```bash
pip install customtkinter pyautogui
python GARGUEL_v1.3.py
```

Or use the included batch files:

```bash
INSTALAR.bat   # install dependencies
INICIAR.bat    # run the bot
```

### Option 2 — Executable

```bash
CREAR_EXE.bat           # builds dist/GARGUEL.exe via PyInstaller
dist\GARGUEL.exe        # run directly, no Python needed
```

---

## Match sequence

| Step | Duration | Action |
|---|---|---|
| Start | 1.5s | Click match start button |
| Difficulty | 2.0s | Select difficulty, confirm |
| Skip intro | 1.5s | 5 rapid clicks to skip cutscene |
| Auto mode | 0.5s | Enable auto-play button |
| First half | 20.0s | Wait |
| Second half | 20.0s | Wait |
| Result screens | 5.0s | Navigate post-match screens, return to menu |
| **Total** | **~50s** | |

---

## Configuration

Click positions are hardcoded for **1920×1080** resolution. To adapt to a different resolution, update `POSITIONS` in `GARGUEL_v1.3.py`:

```python
POSITIONS = {
    'inicio_partido':       (960,  600),
    'seleccionar_dificultad':(960, 540),
    'boton_facil':          (700,  540),
    'boton_normal':         (960,  540),
    'boton_dificil':        (1220, 540),
    'confirmar':            (960,  650),
    'skip_intro':           (1800, 1000),
    'auto_button':          (1850,  50),
    'continuar_1':          (960,  750),
    'continuar_2':          (960,  800),
    'volver_menu':          (960,  900),
}
```

Timing constants (`CLICK_WAIT`, `SCREEN_LOAD`, `MATCH_TIME`, etc.) are defined at the top of the file.

---

## Database schema

Sessions are stored in `garguel_data.db`:

```sql
CREATE TABLE sessions (
    id         INTEGER PRIMARY KEY,
    timestamp  TEXT,
    difficulty TEXT,
    result     TEXT,
    duration   REAL
);
```

---

## Dependencies

```
customtkinter >= 5.2.0
pyautogui     >= 0.9.54
```

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:2b2b00,50:1a1a00,100:0d1117&height=80&section=footer" />
</div>
