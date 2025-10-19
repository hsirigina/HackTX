# How to Run the Interactive Race Simulator

## Quick Start

### Option 1: Demo Mode (RECOMMENDED FOR DEMOS)
**~5-8 decisions only - perfect for demonstrations**

```bash
cd /Users/harsh/Documents/GitHub/HackTX/backend
source venv/bin/activate
python run_interactive_simulator.py --demo
```

**What you'll see:**
- Lap 1: Choose driving style (BALANCED/AGGRESSIVE/QUALI_MODE)
- Lap 21: Pit decision (tire at 85% of max life)
- Lap 44: Second pit decision (if needed)
- Lap 57: Final results with leaderboard

**Demo takes:** ~2-3 minutes

---

### Option 2: Full Mode
**~25 decisions - detailed strategy experience**

```bash
cd /Users/harsh/Documents/GitHub/HackTX/backend
source venv/bin/activate
python run_interactive_simulator.py
```

**What you'll see:**
- Many decision points throughout the race
- Detailed tire state information
- Every strategic opportunity presented

**Full mode takes:** ~10-15 minutes

---

## What You'll Experience

### At Each Decision Point:

```
📍 LAP 21
   Current position: P3
   Tire: SOFT, 21 laps old
   Driving style: AGGRESSIVE
   Total race time: 2034.5s
   Pit stops: 0

🔍 DECISION TRIGGER:
   Tire age: 21/25 laps (84%)
   Compound: SOFT
   Approaching cliff: YES ⚠️
   Past cliff: No

📊 RECOMMENDATION SUMMARY:
   1 Highly Recommended
   1 Recommended
   0 Alternative
   1 Not Recommended

======================================================================
🎯 YOUR OPTIONS:
======================================================================

⭐ OPTION 1: Pit Now - Hard Tires: HIGHLY_RECOMMENDED
   OPTIMAL! Best race time at +35.2s - pit before cliff (lap 25)
   💭 Reasoning: OPTIMAL! Best race time at +35.2s - pit before cliff (lap 25)
   📊 Race time impact: +35.2s
   ⏱️  Lap time impact: -25.0s
   🔥 Tire wear: 0.0x
   ✅ Pros: Fresh HARD tires, One-stop strategy, Avoid cliff penalty
   ❌ Cons: 25s pit loss, Lose track position
   🤖 AI Confidence: HIGHLY_RECOMMENDED

✅ OPTION 2: Pit Now - Medium Tires: RECOMMENDED
   Alternative compound - pit before cliff (lap 25)
   💭 Reasoning: Alternative compound - pit before cliff (lap 25)
   📊 Race time impact: +48.3s
   ⏱️  Lap time impact: -25.0s
   🔥 Tire wear: 0.0x
   ✅ Pros: Fresh MEDIUM tires, Balanced strategy
   ❌ Cons: 25s pit loss, Slower than HARD
   🤖 AI Confidence: RECOMMENDED

❌ OPTION 3: Stay Out - Extend Stint: NOT_RECOMMENDED
   Slower by 2.1s AND will hit tire cliff at lap 25 (4 laps away)
   💭 Reasoning: Slower by 2.1s AND will hit tire cliff at lap 25 (4 laps away)
   📊 Race time impact: -2.1s
   ⏱️  Lap time impact: +1.2s
   🔥 Tire wear: 1.4x
   ✅ Pros: No pit loss, Stay on track
   ❌ Cons: TIRE CLIFF in 4 laps!, Slower overall
   🤖 AI Confidence: NOT_RECOMMENDED

👉 Enter your choice (1-3):
```

### Final Results:

```
🏁 RACE FINISHED!
======================================================================

🏆 YOUR RACE PERFORMANCE:
   Your time:        5564.0s
   Winner's time:    5478.2s (LEC)
   Gap to winner:    +85.8s
   Final position:   P8 / 21

📊 LEADERBOARD (Your Position):
======================================================================
   LEC  Ferrari                     5478.2s
   SAI  Ferrari                     5492.1s
   VER  Red Bull Racing             5504.7s
   NOR  McLaren                     5531.4s
   HAM  Mercedes                    5547.8s
   ALO  Aston Martin                5553.2s
   RUS  Mercedes                    5559.9s
👉 YOU  Your Strategy               5564.0s
   PER  Red Bull Racing             5571.3s
   OCO  Alpine                      5584.7s

📋 YOUR STRATEGY:
   Pit stops: 2
   Pit 1: Lap 23 → HARD tires
   Pit 2: Lap 46 → MEDIUM tires

📋 DECISION TIMELINE:
   Lap  1: Aggressive Driving
   Lap 23: Pit Now - Hard Tires
   Lap 46: Pit Now - Medium Tires
```

---

## Testing Features

### Test 1: Demo Mode Decision Count
```bash
python -c "
from interactive_race_simulator import InteractiveRaceSimulator

sim = InteractiveRaceSimulator(2024, 'Bahrain', 57, 'VER', demo_mode=True)
sim.start_race()

decision_count = 0
for lap in range(1, 58):
    if sim.should_offer_decision(lap):
        decision_count += 1

print(f'Demo mode decisions: {decision_count}')
"
```

Expected: 5-8 decisions

### Test 2: Full Mode Decision Count
```bash
python -c "
from interactive_race_simulator import InteractiveRaceSimulator

sim = InteractiveRaceSimulator(2024, 'Bahrain', 57, 'VER', demo_mode=False)
sim.start_race()

decision_count = 0
for lap in range(1, 58):
    if sim.should_offer_decision(lap):
        decision_count += 1

print(f'Full mode decisions: {decision_count}')
"
```

Expected: ~25 decisions

### Test 3: Dynamic Behavior (User Ignores AI)
```bash
python test_continuous_stay_out.py
```

Shows what happens when user keeps choosing "Stay Out" even when AI says NOT_RECOMMENDED.

### Test 4: Pit Window Selector
```bash
python pit_window_selector.py
```

Shows the new pit window timeline UX.

---

## Key Files

### Main Files
- `run_interactive_simulator.py` - Main entry point (run this!)
- `interactive_race_simulator.py` - Core simulator with dynamic AI
- `tire_model.py` - Physics model with tire cliff penalty

### New Features
- `pit_window_selector.py` - New UX for pit timing (timeline selector)
- `test_continuous_stay_out.py` - Test dynamic decision behavior
- `test_dynamic_ai.py` - Test full race with auto AI following

### Documentation
- `DYNAMIC_AI_IMPROVEMENTS.md` - Technical details of dynamic AI
- `UX_IMPROVEMENTS.md` - Answers to your 3 questions
- `AI_STRATEGY_IMPROVEMENTS.md` - Original strategy fixes

---

## Tips for Best Demo Experience

1. **Use Demo Mode** (`--demo` flag)
   - Only 5-8 decisions
   - Keeps demo moving
   - Shows critical moments

2. **Follow Highly Recommended (⭐)**
   - Best chance to beat VER
   - Shows AI working correctly

3. **Or Deliberately Ignore AI**
   - Pick NOT_RECOMMENDED options
   - Shows tire cliff penalty
   - Demonstrates dynamic response

4. **Show the Decision Context**
   - Point out tire age percentage
   - Explain why decision triggered
   - Show AI adapting to choices

---

## Troubleshooting

### Error: "Module not found: fastf1"
```bash
source venv/bin/activate
pip install fastf1
```

### Error: "No such file: race_data.pkl"
This is normal - FastF1 will download data on first run (takes ~30 seconds)

### Race takes too long
Use `--demo` flag for faster experience

### Want to test without interaction
```bash
python test_dynamic_ai.py  # Auto-follows AI recommendations
```

---

## Next Steps

### For Frontend Integration:

1. Import the simulator:
```python
from interactive_race_simulator import InteractiveRaceSimulator

sim = InteractiveRaceSimulator(2024, 'Bahrain', 57, 'VER', demo_mode=True)
```

2. Generate decisions as JSON:
```python
options = sim.generate_decision_options(current_lap)
return json.dumps([{
    'id': opt.option_id,
    'title': opt.title,
    'description': opt.description,
    'confidence': opt.ai_confidence,
    'race_impact': opt.predicted_race_time_impact,
    'reasoning': opt.reasoning,
    'pros': opt.pros,
    'cons': opt.cons
} for opt in options])
```

3. Use Pit Window Selector:
```python
from pit_window_selector import PitWindowSelector

selector = PitWindowSelector(sim.tire_model, sim.total_laps)
window = selector.generate_pit_window(...)
# Returns timeline data for React component
```
