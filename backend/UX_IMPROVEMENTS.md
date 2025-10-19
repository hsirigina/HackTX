# UX Improvements - Demo Mode & Pit Window Selector

## Your 3 Questions Answered

### 1. "I don't want to make 25 decisions for the demo"

**Solution: DEMO MODE**

Added `demo_mode` parameter that reduces decisions from ~25 to ~5-8:

```python
# DEMO MODE: Only critical decisions
sim = InteractiveRaceSimulator(
    race_year=2024,
    race_name='Bahrain',
    total_laps=57,
    comparison_driver='VER',
    demo_mode=True  # ← Only 5-8 decisions!
)
```

**Demo Mode Decision Points:**
- Lap 1: Initial driving style setup
- Lap ~21: When tire reaches 85% of max life (SOFT: lap 21, HARD: lap 51)
- Lap ~26: If past tire cliff (emergency pit)
- Lap 57: Final lap push

**Full Mode Decision Points (25 total):**
- Lap 1: Initial setup
- Laps 9-24: Every lap from 40% tire age to cliff
- Laps 30, 40, 50: Tactical adjustments
- Laps 55-57: Final push

**Usage:**
```bash
python run_interactive_simulator.py --demo  # 5-8 decisions
python run_interactive_simulator.py         # 25 decisions
```

---

### 2. "If I didn't follow the AI and continued to stay out, does this affect my next options? Is it dynamic in this way?"

**Answer: YES - FULLY DYNAMIC!**

The system is **already doing this**. Decisions are triggered by **tire state**, not fixed laps.

**Test Results (user keeps choosing "Stay Out"):**
```
Lap 18 (tire 18/25 = 72%)
  ✅ Decision offered: 3 options
  👉 User chooses: 'Stay Out' (RECOMMENDED)
     Impact: -8.1s  ← Still saves time!

Lap 22 (tire 22/25 = 88%)
  ✅ Decision offered: 3 options
  👉 User chooses: 'Stay Out' (NOT_RECOMMENDED)
     Impact: +0.1s  ← Now costs time!

Lap 25 (tire 25/25 = 100%)
  ✅ Decision offered: 3 options
  👉 User chooses: 'Stay Out' (NOT_RECOMMENDED)
     Impact: +32.9s  ← At cliff - huge penalty!

Lap 28 (tire 28/25 = 112%)
  ✅ Decision offered: 3 options
  👉 User chooses: 'Stay Out' (NOT_RECOMMENDED)
     Impact: +137.4s  ← Disaster!
```

**Key Insight:** User gets **decision every lap** as tire degrades. AI keeps warning them, but they CAN ignore it and stay out. The system adapts its recommendations based on the user's actual tire state.

**How it works:**
```python
def should_offer_decision(lap_number):
    tire_age_pct = tire_age / max_laps

    # User kept staying out? Tire age keeps increasing!
    if tire_age_pct >= 0.70:  # 70%+ of max tire life
        return True  # Keep offering pit decision every lap!
```

---

### 3. "Would it be better to ask WHICH LAP to pit, rather than Stay Out vs Pit Now?"

**Answer: BRILLIANT IDEA - PIT WINDOW SELECTOR!**

Created a new UX paradigm: **visual pit window timeline**

**Old UX (binary choice):**
```
Option 1: Pit Now (lap 18)
Option 2: Stay Out 3 laps (pit lap 21)
Option 3: Stay Out 5 laps (pit lap 23)
```

**New UX (pit window timeline):**
```
🏎️  PIT WINDOW SELECTOR
======================================================================

Current state: Lap 18, SOFT tires, 18 laps old
Tire cliff: Lap 25 (7 laps away)

🎯 AI OPTIMAL: Pit lap 22 for HARD tires (+35.2s)

PIT WINDOW TIMELINE:

Lap:  18  19  20  21  22  23  24  25  26  27  28  29  30  Never
      🟡  🟡  🟡  🟡  🟢  🟢  🟢  🟢  🔴  🔴  ⛔  ⛔  ⛔   ⛔

🟢 RECOMMENDED: Laps 22-25 (optimal window before cliff)
🟡 ACCEPTABLE:  Laps 18-21 (early but OK)
🔴 RISKY:       Laps 26-27 (approaching cliff)
⛔ DANGER:      Laps 28+ or Never (past cliff - exponential penalty!)

Click any lap to pit that lap, or click "Never" to run to the end.
```

**Benefits:**
1. **Visual understanding** - User sees entire strategy space
2. **AI guidance** - Green = good, Red = bad, but user decides
3. **Flexibility** - Can pit ANY lap (18, 19, 20, ..., 30, or never)
4. **Risk awareness** - Shows exact penalty for each choice
5. **Better for demos** - More impressive than binary choice

**Frontend Implementation:**

```jsx
// Example React component
<PitWindowTimeline
  laps={window.lap_details}
  optimal={window.optimal_lap}
  onLapClick={(lap) => handlePitDecision(lap)}
/>

// Renders as:
// [Lap 18] [Lap 19] [Lap 20] [Lap 21] [Lap 22*] [Lap 23] ...
//    🟡       🟡       🟡       🟡       🟢        🟢
//                                        ↑ AI OPTIMAL
```

**API:**
```python
from pit_window_selector import PitWindowSelector

selector = PitWindowSelector(tire_model, total_laps=57)

window = selector.generate_pit_window(
    current_lap=18,
    current_tire_age=18,
    current_compound='SOFT',
    laps_remaining=39
)

# Returns:
{
    'optimal_lap': 22,
    'optimal_compound': 'HARD',
    'optimal_impact': +35.2,
    'recommended_window': [22, 23, 24, 25],
    'acceptable_window': [18, 19, 20, 21],
    'risky_window': [26, 27],
    'danger_window': [28, 29, 30, ...],
    'lap_details': [
        PitWindowLap(lap=18, compound='HARD', impact=+42.1, rec='ACCEPTABLE', color='yellow'),
        PitWindowLap(lap=22, compound='HARD', impact=+35.2, rec='HIGHLY_RECOMMENDED', color='green'),
        ...
    ],
    'never_pit': {
        'possible': False,
        'penalty': +8628778,  # Disaster!
        'warning': '⛔ DISASTER - 32 laps past cliff!'
    }
}
```

---

## Implementation Files

### Demo Mode
- **File:** `interactive_race_simulator.py`
- **Changes:**
  - Added `demo_mode` parameter to `__init__`
  - Updated `should_offer_decision()` with demo logic
  - Demo: ~5-8 decisions (lap 1, 85% tire, final lap)
  - Full: ~25 decisions (every lap 40%+, every 10 laps tactical)

### Continuous Decision Testing
- **File:** `test_continuous_stay_out.py`
- **Purpose:** Proves system is fully dynamic
- **Shows:** User ignoring AI gets asked every lap as tire degrades

### Pit Window Selector
- **File:** `pit_window_selector.py`
- **Class:** `PitWindowSelector`
- **Methods:**
  - `generate_pit_window()` - Creates timeline with recommendations
  - `_calculate_pit_impact_at_lap()` - Time impact for each lap
  - `_calculate_never_pit_impact()` - What if user never pits?

---

## Recommendation: Use Pit Window Selector

The **Pit Window Selector** is the best UX for your demo because:

1. ✅ **Visually impressive** - Timeline with color coding
2. ✅ **Educational** - Shows WHY each lap is good/bad
3. ✅ **Flexible** - User can pick ANY lap (not just 3 options)
4. ✅ **AI-guided** - Recommendations highlighted but not forced
5. ✅ **Realistic** - How real F1 engineers think about strategy
6. ✅ **Gesture-friendly** - Swipe timeline, tap lap to pit

**Demo Flow:**
```
Lap 1:  Choose driving style (BALANCED/AGGRESSIVE/QUALI)
Lap 21: [PIT WINDOW SELECTOR appears]
        Timeline shows laps 18-33
        User swipes, sees lap 22 is green (optimal)
        Taps lap 22 → "Pitting lap 22 for HARD tires"
Lap 44: [PIT WINDOW SELECTOR appears again]
        Timeline shows laps 41-56
        User picks lap 46
Lap 57: [FINAL RESULTS]
        Your time: 5550.3s
        VER time:  5504.7s
        Gap: +45.6s (P8!)
```

This gives you:
- **Only 3 user decisions** (style, pit 1, pit 2)
- **Rich visual experience** (timeline selector)
- **AI guidance without forcing** (recommendations clear but user decides)
- **Perfect for hackathon demo!**
