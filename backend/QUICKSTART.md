# 🏎️ Interactive Race Simulator - Quick Start

## Run It Now!

### Easiest Way (Menu)
```bash
./run_demo.sh
```

Then choose:
- **1** for Demo Mode (5-8 decisions, perfect for demos)
- **2** for Full Mode (25 decisions, detailed strategy)

---

### Direct Commands

**Demo Mode (RECOMMENDED):**
```bash
cd /Users/harsh/Documents/GitHub/HackTX/backend
source venv/bin/activate
python run_interactive_simulator.py --demo
```

**Full Mode:**
```bash
cd /Users/harsh/Documents/GitHub/HackTX/backend
source venv/bin/activate
python run_interactive_simulator.py
```

---

## What to Expect

### Demo Mode (~3 minutes)
- **Lap 1:** Choose driving style
- **Lap 21:** First pit decision (tire at 85% worn)
- **Lap 44:** Second pit decision
- **Lap 57:** Final results + leaderboard

### Example Decision:
```
⭐ OPTION 1: Pit Now - Hard Tires (HIGHLY_RECOMMENDED)
   OPTIMAL! Best race time at +35.2s - pit before cliff
   Race impact: +35.2s | Lap impact: -25.0s

✅ OPTION 2: Pit Now - Medium Tires (RECOMMENDED)
   Alternative compound - pit before cliff
   Race impact: +48.3s | Lap impact: -25.0s

❌ OPTION 3: Stay Out (NOT_RECOMMENDED)
   Slower by 2.1s AND will hit tire cliff in 4 laps!
   Race impact: -2.1s | Lap impact: +1.2s

👉 Enter your choice (1-3):
```

---

## Tips

✅ **Follow ⭐ HIGHLY_RECOMMENDED** - Best chance to finish top 10

🎮 **Or ignore AI** - Pick ❌ NOT_RECOMMENDED to see tire cliff penalty!

📊 **Watch the numbers** - Tire age % shows when you MUST pit

---

## What Changed?

### ✅ Fully Dynamic AI
- **Before:** Hardcoded 13 decision laps
- **After:** 25+ decisions triggered by tire state

### ✅ Smart Recommendations
- **Before:** "Stay Out" recommended even when slower
- **After:** AI recommends actual fastest option

### ✅ Demo Mode
- **New:** Only 5-8 critical decisions for quick demos

---

## Files Reference

- `run_interactive_simulator.py` - Main program (run this!)
- `interactive_race_simulator.py` - Core AI logic
- `pit_window_selector.py` - New timeline UX (for frontend)
- `RUN_INSTRUCTIONS.md` - Full documentation
- `UX_IMPROVEMENTS.md` - Answers to your 3 questions
