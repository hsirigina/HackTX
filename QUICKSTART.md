# F1 Multi-Agent Race Strategy System - Quick Start Guide

## What You've Built

A complete AI-powered F1 race strategy system with:
- ✅ **Race Replay System** - Streams historical F1 data to Supabase
- ✅ **3 AI Agents** - Tire Strategist, Competitor Tracker, Coordinator
- ✅ **Tire Degradation Model** - Ported from MATLAB, calculates optimal pit windows
- ✅ **Arduino Driver Display** - LCD showing pit countdown and alerts
- ✅ **Real-time Database** - Supabase with 5 tables for race data

## Prerequisites

### 1. Get Google Gemini API Key (FREE)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### 2. Add API Key to Environment
Edit `.env` file:
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

## Running the Demo

### Option 1: Full AI Demo (Recommended)

This runs the complete system with AI agents analyzing the race:

```bash
cd backend
source venv/bin/activate
python demo.py
```

**What you'll see:**
- Race data streaming lap-by-lap
- Tire Agent analyzing tire degradation
- Competitor Agent tracking opponents
- Coordinator synthesizing recommendations
- Recommendations saved to Supabase

**Demo focuses on**: Monaco 2024, laps 60-78 (Leclerc's winning final stint)

### Option 2: Race Replay Only (No AI)

Just stream race data without agent analysis:

```bash
cd backend
source venv/bin/activate
python race_replay.py
```

### Option 3: Test Arduino Display

Test the driver display without a full race:

```bash
cd backend
source venv/bin/activate
python arduino_controller.py
```

**Requirements:**
- Arduino Nano/Uno connected via USB
- 16x2 LCD with I2C module wired to Arduino
- Upload `arduino/driver_display/driver_display.ino` first

## System Architecture

```
┌─────────────────┐
│   FastF1 API    │  Historical F1 race data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Race Replay    │  Streams data lap-by-lap
│  (Python)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Supabase     │  Real-time database
│   PostgreSQL    │  (5 tables)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Race Monitor   │  Polls for new laps
│  (Python)       │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌──────────────┐   ┌─────────────────┐   ┌──────────────┐
│ Tire Agent   │   │ Competitor      │   │ Coordinator  │
│ (Gemini)     │   │ Agent (Gemini)  │   │ (Gemini)     │
└──────────────┘   └─────────────────┘   └──────────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ Recommendations │
                  │ (Supabase)      │
                  └─────────────────┘
```

## What Each Component Does

### Backend Scripts

| File | Purpose |
|------|---------|
| `race_replay.py` | Loads historical F1 races from FastF1 and streams to Supabase |
| `race_monitor.py` | Monitors Supabase for new laps and triggers AI agent analysis |
| `demo.py` | Runs both replay and monitor together for full demo |
| `agents.py` | 3 AI agents (Tire, Competitor, Coordinator) using Gemini |
| `tire_model.py` | Tire degradation model ported from MATLAB |
| `arduino_controller.py` | Controls Arduino driver display via serial |

### Database Tables (Supabase)

| Table | Purpose |
|-------|---------|
| `lap_times` | Lap-by-lap timing data for all drivers |
| `tire_data` | Tire compound, age, degradation per lap |
| `pit_stops` | Pit stop times and durations |
| `race_positions` | Driver positions each lap |
| `agent_recommendations` | AI agent strategy recommendations |

## Customizing the Demo

### Change Race
Edit `backend/demo.py`:
```python
START_LAP = 1    # Start from lap 1
END_LAP = 78     # Full race
```

### Change Driver Focus
```python
FOCUSED_DRIVER = "VER"  # Verstappen instead of Leclerc
```

### Change Replay Speed
```python
LAPS_PER_SECOND = 1.0  # Faster: 1 lap per second
```

### Analyze Different Race
In `race_replay.py`:
```python
replay.load_race(2024, 'Singapore', 'R')  # Singapore instead of Monaco
```

## Viewing Results

### Check Supabase
1. Go to https://supabase.com/dashboard
2. Select your `hackTX` project
3. Click "Table Editor"
4. View `agent_recommendations` table to see AI analysis

### Query Recommendations
```sql
SELECT
  lap_number,
  agent_name,
  recommendation_type,
  confidence_score,
  reasoning
FROM agent_recommendations
WHERE race_id = 'monaco_2024'
ORDER BY lap_number DESC;
```

## Troubleshooting

### "No module named 'fastf1'"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "GOOGLE_API_KEY not set"
1. Check `.env` file exists
2. Make sure API key is on the line: `GOOGLE_API_KEY=your_key`
3. No quotes needed around the key

### "No Arduino detected"
- Arduino not connected? System will still work, just no LCD display
- Check USB connection
- Upload `driver_display.ino` using Arduino IDE first
- Verify serial port in Device Manager (Windows) or `ls /dev/tty*` (Mac/Linux)

### Race data loading slow
- First time loading a race downloads ~100MB of data
- FastF1 caches it in `data/cache/` for next time
- Be patient, Monaco 2024 takes ~2-3 minutes first time

## Next Steps (For Hackathon)

### 1. Build React Dashboard
Create frontend to visualize:
- Real-time race positions
- Agent status (green/yellow/red)
- Top 3 strategy recommendations
- Win probability charts

### 2. Add Gesture Recognition
Use MediaPipe to detect:
- Fist pump = Confirm strategy
- Swipe right = View aggressive options
- Swipe left = View conservative options

### 3. Connect Arduino Display
Integrate `arduino_controller.py` into `race_monitor.py`:
```python
from arduino_controller import ArduinoController

arduino = ArduinoController()

# When coordinator decides to pit:
arduino.set_pit_countdown(3)
```

### 4. Polish Demo Narrative
Practice explaining:
- "Agents autonomously monitor the race"
- "Tire Agent detected degradation cliff approaching"
- "Agents split 2-1, Coordinator synthesizes final recommendation"
- "Engineer confirms with gesture, driver sees countdown on display"

## File Structure

```
HackTX/
├── backend/
│   ├── agents.py              # AI agents (Gemini)
│   ├── tire_model.py          # Tire degradation model
│   ├── race_replay.py         # FastF1 → Supabase
│   ├── race_monitor.py        # Monitor + agent orchestration
│   ├── arduino_controller.py  # Arduino serial control
│   ├── demo.py                # Full demo script
│   ├── requirements.txt       # Python dependencies
│   └── venv/                  # Virtual environment
├── arduino/
│   └── driver_display/
│       └── driver_display.ino # Arduino LCD code
├── data/
│   ├── cache/                 # FastF1 cache
│   └── race-strategy-analysis/# MATLAB source repo
├── .env                       # Environment variables
├── .env.example               # Template
├── PRD_Full_System.md         # Complete documentation
├── PRD_Arduino_Driver_Display.md
└── QUICKSTART.md              # This file
```

## Demo Day Tips

1. **Pre-load race data** - Run `race_replay.py` once before demo to cache data
2. **Test API key** - Verify Gemini API works before presenting
3. **Arduino backup** - If Arduino fails, show simulated output in terminal
4. **Pick exciting laps** - Start at lap 60+ for Monaco (close finish)
5. **Speed up replay** - Use `LAPS_PER_SECOND = 2.0` for faster demo

## Support

- **FastF1 Docs**: https://docs.fastf1.dev/
- **Gemini API**: https://ai.google.dev/docs
- **Supabase Docs**: https://supabase.com/docs
- **Arduino LCD**: https://www.arduino.cc/reference/en/libraries/liquidcrystal-i2c/

---

Built for HackTX 2024
