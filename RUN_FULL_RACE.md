# 🏁 Run Full Bahrain 2024 Race - AI Strategy Test

## What This Does

Runs the complete Bahrain 2024 race (all 57 laps) and validates if your AI strategy matches reality:

- **Actual race**: Leclerc pitted on **laps 12 and 35**
- **AI strategy**: Will it predict these same pit windows?

## Step-by-Step Instructions

### 1. Clear Old Data (Monaco)
```bash
cd backend
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Clear Monaco data
tables = ['lap_times', 'tire_data', 'pit_stops', 'race_positions', 'agent_recommendations', 'agent_status']
for table in tables:
    supabase.table(table).delete().eq('race_id', 'monaco_2024').execute()
    print(f'Cleared {table}')

print('✅ Old Monaco data cleared')
"
```

### 2. Start Race Replay (Terminal 1)
This streams all 57 laps to Supabase at 1 lap every 2 seconds (≈ 2 minutes total):

```bash
cd backend
python race_replay.py
```

**Expected output:**
```
🏎️  Loading 2024 Bahrain R...
🗑️  Clearing existing data...
🎬 Starting replay of Bahrain 2024 (57 laps)...
   Leclerc 2-stop strategy: Pit laps 12 and 35

📍 LAP 1 - Streaming...
📍 LAP 2 - Streaming...
...
✅ Replay complete! Pushed 57 laps to Supabase.
```

### 3. Start Race Monitor (Terminal 2)
This runs AI analysis on each lap:

```bash
cd backend
python race_monitor_v2.py LEC bahrain_2024
```

**What to watch for:**
- Around **lap 10-12**: Should see "PIT_NOW" or "PIT_SOON" recommendations
- Around **lap 33-35**: Should see second pit window recommendation
- Watch the reasoning - does it make sense?

**Expected output:**
```
📍 LAP 12 - LEC
⏱️  Lap time: 96.234s
🏁 Position: P4
🔧 Tires: MEDIUM (11 laps)

🚨 Events Detected:
   🟡 [HIGH] Tire degradation increasing - consider pit window

🤖 Calling AI Coordinator...
📋 AI RECOMMENDATION (Lap 12):
   Type: PIT_NOW
   Urgency: CRITICAL
   Driver: "Box box! Optimal window. MEDIUM → HARD"
   Reasoning: "Tire model predicts optimal pit on lap 12..."
```

### 4. Start Frontend (Terminal 3)
Watch the live dashboard:

```bash
cd ../frontend
npm run dev
```

Open: http://localhost:5173

**What to see:**
- Live lap counter (1 → 57)
- Tire age increasing, then resetting after pits
- AI recommendations changing lap-by-lap
- Around lap 12 & 35: Big strategy updates

### 5. Analyze Results (After Race Completes)
```bash
cd backend
python analyze_strategy_performance.py
```

**Expected output:**
```
🔍 AI STRATEGY ANALYSIS: BAHRAIN_2024 - LEC
============================================================

📊 ACTUAL RACE PIT STOPS:
   Lap 12: Pit stop (25.0s)
   Lap 35: Pit stop (25.0s)

🤖 AI RECOMMENDATIONS:
   Lap 10: PIT_SOON - Pit in 2 laps. Conserve tires.
   Lap 11: PIT_SOON - Pit in 1 lap. Window approaching.
   Lap 12: PIT_NOW - Box box! Optimal window.
   Lap 33: PIT_SOON - Pit in 2 laps. Conserve tires.
   Lap 35: PIT_NOW - Box box! Optimal window.

============================================================
✅ ALIGNMENT CHECK:
============================================================

✅ Actual pit lap 12:
   AI said PIT_NOW on lap(s): [12]
   🎯 MATCH! AI predicted within 3 laps

✅ Actual pit lap 35:
   AI said PIT_NOW on lap(s): [35]
   🎯 MATCH! AI predicted within 3 laps

============================================================
🏁 FINAL VERDICT:
============================================================

   Actual pit stops: 2
   AI predictions (within 3 laps): 2/2
   Accuracy: 100%

   ✅ EXCELLENT - AI strategy closely matches optimal race strategy!
```

## What Success Looks Like

✅ **AI predicts lap 12 pit**: Recommends PIT_NOW around laps 10-12
✅ **AI predicts lap 35 pit**: Recommends PIT_NOW around laps 33-37
✅ **Reasoning makes sense**: References tire degradation, optimal windows
✅ **Frontend updates live**: Shows tire age reset after pits
✅ **No false positives**: Doesn't recommend random extra pit stops

## If Something's Wrong

**Problem**: AI recommends pitting every 5 laps
- **Cause**: Tire model parameters too aggressive
- **Fix**: Check tire_model.py wear rates

**Problem**: AI never recommends pitting
- **Cause**: Event detector thresholds too high
- **Fix**: Check data_agents.py event triggers

**Problem**: Frontend shows lap 1/78 instead of 1/57
- **Fix**: Already updated, clear browser cache

## Quick Test (Just Lap 10-15)

If you want to test just the first pit window quickly:

```bash
# Edit race_replay.py line 278-279:
replay.replay(
    start_lap=8,   # Start just before first pit
    end_lap=15,    # End just after
    focused_driver='LEC'
)
```

Then run terminals 1, 2, 3 as above. Should see first pit recommendation in ~14 seconds.

## Time Estimate

- **Full race**: ~2 minutes (57 laps × 2 seconds each)
- **Quick test**: ~14 seconds (8 laps)
- **Analysis**: Instant (just queries database)

## What This Proves

If accuracy is 100%, you can confidently say:

> "Our AI race strategy system successfully predicted both pit stops in the Bahrain Grand Prix with 100% accuracy, matching Ferrari's actual winning strategy."

That's your hackathon demo gold! 🏆
