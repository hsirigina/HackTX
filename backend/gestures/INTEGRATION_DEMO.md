# Gesture Strategy Dashboard Integration Demo

## What This Does

This demo shows how gestures control a **real race strategy decision system** with multiple scenarios that you can browse and select using hand gestures.

## Run the Demo

```bash
cd backend/gestures
python gesture_strategy_demo.py
```

## The Scenario

**Monaco 2024, Lap 65:**
- You're managing Charles Leclerc (P1)
- Oscar Piastri is P2, only 0.8s behind and closing fast (0.3s/lap)
- Old tires (64 laps on HARD compound)
- **Critical decision point!**

## 3 Strategy Scenarios

You can swipe through these options:

### 1. Aggressive Undercut 🔴
- **Action**: PIT NOW
- **Tires**: SOFT
- **Pit Lap**: 65 (this lap!)
- **Reasoning**: Undercut Piastri before he pits. Push on outlap.
- **Urgency**: HIGH

### 2. Defensive Stay Out 🔵
- **Action**: STAY OUT
- **Tires**: Keep HARD
- **Pit Lap**: 70 (5 more laps)
- **Reasoning**: Track position critical at Monaco. Force Piastri to pit first.
- **Urgency**: MEDIUM

### 3. Conservative Medium 🟡
- **Action**: PIT SOON
- **Tires**: MEDIUM
- **Pit Lap**: 67 (in 2 laps)
- **Reasoning**: Balanced approach. Safer than SOFT, better than staying out.
- **Urgency**: MEDIUM

## How Gestures Work

### ➡️ Swipe Right - Next Scenario
- Move your **open hand** from LEFT to RIGHT
- Cycles through strategy options (1 → 2 → 3 → 1...)
- Dashboard updates instantly

### ⬅️ Swipe Left - Previous Scenario
- Move your **open hand** from RIGHT to LEFT
- Cycles backwards (3 → 2 → 1 → 3...)
- Dashboard updates instantly

### 👍 Thumbs Up - Lock In Strategy
- Make a **fist** with **thumb pointing UP**
- **Confirms and locks** the currently displayed strategy
- Green "STRATEGY LOCKED" banner appears
- Prints confirmation to console

### ✌️ Peace Sign - Show Details
- **Index + middle fingers** extended (V shape)
- Toggles **detailed breakdown** panel
- Shows:
  - Tire life remaining
  - Pace delta vs competitor
  - Track position importance
  - Alternative options

## What You'll See

### Main Dashboard Panel (Right Side)
- **Strategy Name** (color-coded by urgency)
- **Quick Info**:
  - Action type (PIT_NOW, STAY_OUT, etc.)
  - Tire compound recommendation
  - Target pit lap
  - Urgency level
  - AI confidence score
- **Strategy Reasoning** (5 lines of explanation)
- **Detailed Breakdown** (when you make peace sign)
- **Locked Indicator** (when you thumbs up)

### Hand Tracking (Full Frame)
- Your webcam feed with hand landmarks
- Colorful dots and lines showing hand joints
- Real-time tracking at 30 FPS

### Action Feedback (Bottom Left)
- Shows last gesture action for 3 seconds
- Examples:
  - "→ Next: Aggressive Undercut"
  - "✅ LOCKED: Conservative Medium"
  - "✌️ Details SHOWING"

## Console Output

The system prints to console when you perform gestures:

```
▶️  SWIPE RIGHT → Next scenario: Defensive Stay Out

◀️  SWIPE LEFT ← Previous scenario: Aggressive Undercut

👍 THUMBS UP → STRATEGY LOCKED!
   📋 Executing: Aggressive Undercut
   🏁 Action: PIT_NOW
   🛞 Tires: SOFT
   📍 Pit Lap: 65

✌️  PEACE SIGN → Details SHOWING
```

## Integration with Real System

### Current Demo
- **Mock scenarios** - 3 pre-defined strategy options
- Simulates Monaco lap 65 critical decision

### Real Integration (Next Step)
Would connect to:
1. **`coordinator_agent.py`** - Gets AI strategy recommendations
2. **`race_monitor_v2.py`** - Monitors live race data
3. **`data_agents.py`** - Gets tire, pace, position data
4. **Arduino display** - Shows locked strategy to pit crew

### How It Would Work

```python
# Real integration flow:

# 1. Race Monitor detects critical event
events = monitor.check_events(current_lap)

# 2. AI Coordinator generates multiple scenarios
scenarios = coordinator.generate_scenarios(events, lap_data)

# 3. Gesture controller loads scenarios
controller.scenarios = scenarios

# 4. Engineer uses gestures to browse and select
# (Swipe right/left to review options)

# 5. Engineer locks in choice with thumbs up
# (Triggers actual pit call + Arduino update)

# 6. Peace sign shows detailed AI reasoning
# (Explains why this strategy vs others)
```

## Tips

1. **Sit 2-3 feet** from your Mac camera
2. **Good lighting** - face a window or lamp
3. **Clear background** - simple background works best
4. **Swipes**: Use open hand, move smoothly across frame
5. **Static gestures**: Hold for 0.5 seconds
6. **Wait 1 second** between gestures (cooldown)

## Quit

Press **'q'** to exit the demo.

## What This Proves

✅ **Gestures work** - Reliable detection with real actions  
✅ **UI Updates** - Dashboard responds immediately to gestures  
✅ **Multiple scenarios** - Can browse through different options  
✅ **Confirmation** - Lock in prevents accidental selection  
✅ **Details on demand** - Peace sign reveals deeper analysis  
✅ **Ready for integration** - Architecture supports real race data  

This is a **working prototype** of the full system! 🏎️💨

