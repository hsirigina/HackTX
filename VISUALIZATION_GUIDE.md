# Visual Race Comparison Guide

## 🎯 What Changed

Instead of just showing numbers, the frontend now displays a **split-screen live race comparison** showing:
- **Left side:** AI Strategy (follows coordinator recommendations)
- **Right side:** Baseline (no strategy, never pits)
- **Animated cars** moving around an oval track in real-time
- **Live time difference** showing who's ahead and by how much

## 🏎️ Visual Elements

### Split-Screen Tracks
- Each side shows a circular/oval track representation
- Car emoji (🏎️) animates around the track based on lap progress
- Green border = AI Strategy | Red border = Baseline
- Start/finish line marked on the left side

### Live Statistics
Each side shows:
- **Cumulative time** (total race time so far)
- **Current tire compound** (HARD, MEDIUM, SOFT)
- **Tire age** (laps on current tires)
- **Pit stop status** (has pitted yes/no, which lap)

### Time Difference Banner
- Shows who's ahead and by how much
- Converts time difference to "car lengths" for intuitive understanding
- Green = AI ahead | Red = AI behind

### Progress Bar
- Shows current lap / total laps
- Visual indication of race progress

## 📊 How It Works

### Backend (race_comparison_engine.py)
The comparison engine runs in parallel with the race monitor:

1. **Every lap**, it simulates BOTH strategies:
   - **AI Strategy:** Checks recommendations, pits when AI says to
   - **Baseline:** Never pits (Monaco context: track position > tire performance)

2. **Calculates lap times** using tire degradation model:
   - Fresh tires = faster laps
   - Worn tires = slower laps (degradation increases)
   - Pit stop = 25 second time loss

3. **Saves to database** (`race_comparison` table):
   - Both cumulative times
   - Tire states
   - Pit stop status

### Frontend (RaceComparison.jsx)
The component polls Supabase every 2 seconds and:

1. **Fetches comparison data** from `race_comparison` table
2. **Animates car positions** around track based on lap progress
3. **Updates live stats** (time, tires, pit status)
4. **Shows time difference** with visual indicator

## 🎬 Demo Flow

### For Hackathon Judges:

1. **Start race replay:**
   ```bash
   cd backend
   python race_replay.py
   ```

2. **Start race monitor:**
   ```bash
   python race_monitor_v2.py LEC monaco_2024
   ```

3. **Open frontend:**
   ```bash
   cd ../frontend
   npm run dev
   ```

4. **Watch the visualization:**
   - Top section shows split-screen comparison
   - Cars animate lap-by-lap
   - Time difference updates in real-time
   - See AI strategy impact visually

### What Judges Will See:

**Lap 1-30:** Both strategies roughly equal (fresh tires)

**Lap 30-50:** Baseline starts slowing (tire degradation), AI may pit if recommended

**Lap 50-78:** Clear difference emerges:
- If AI pitted: Fresh tires compensate for 25s pit loss
- If AI stayed out (Monaco): Track position maintained

**End result:** Time difference banner shows total advantage

## 🔧 Customization

### Change Strategy Behavior

Edit `race_comparison_engine.py`:

```python
def should_ai_pit(self, current_lap: int, recommendation: Dict) -> bool:
    """Determine if AI strategy should pit this lap"""
    # Customize pit decision logic here
    if rec_type == 'PIT_NOW':
        return True
    # Add your own logic
```

### Change Baseline Behavior

```python
# In simulate_lap() method
# Currently: baseline never pits
# To add pit stop at lap 40:
if current_lap == 40 and not self.baseline_state['has_pitted']:
    self.execute_pit_stop(self.baseline_state, current_lap, 'MEDIUM')
```

### Adjust Visual Track

Edit `RaceComparison.jsx`:

```javascript
// Change track shape (currently circular)
style={{
  top: `${50 + 35 * Math.sin(...)}%`,  // Adjust radius (35)
  left: `${50 + 35 * Math.cos(...)}%`,
}}

// Or make it Monaco-shaped (winding oval)
```

## 📋 Database Schema

Create `race_comparison` table in Supabase:

```sql
CREATE TABLE race_comparison (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  driver_name TEXT NOT NULL,
  lap_number INTEGER NOT NULL,

  -- AI Strategy state
  ai_cumulative_time FLOAT NOT NULL,
  ai_tire_compound TEXT NOT NULL,
  ai_tire_age INTEGER NOT NULL,
  ai_has_pitted BOOLEAN DEFAULT FALSE,
  ai_pit_lap INTEGER,

  -- Baseline state
  baseline_cumulative_time FLOAT NOT NULL,
  baseline_tire_compound TEXT NOT NULL,
  baseline_tire_age INTEGER NOT NULL,
  baseline_has_pitted BOOLEAN DEFAULT FALSE,
  baseline_pit_lap INTEGER,

  -- Meta
  time_difference FLOAT,  -- ai - baseline
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Unique constraint
  UNIQUE(race_id, driver_name, lap_number)
);
```

## 🎨 Visual Improvements (Future Ideas)

1. **Monaco track shape:** Replace oval with actual Monaco circuit shape
2. **Multiple cars:** Show other drivers as background context
3. **Sector highlights:** Color-code track sections (Sector 1, 2, 3)
4. **3D perspective:** Tilt track for depth effect
5. **Pit lane animation:** Show car entering/exiting pit lane
6. **Tire wear indicator:** Visual degradation (color fading)
7. **Speed trails:** Motion blur effect on faster car
8. **Sound effects:** Engine sounds, pit stop sounds

## 📈 Key Metrics for Demo

**What judges care about:**

1. **Visual clarity:** Is it obvious which strategy is better?
2. **Real-time updates:** Does it feel live and responsive?
3. **Strategic insight:** Can they understand WHY AI is ahead/behind?
4. **Engagement:** Is it more compelling than just numbers?

**Success criteria:**
- ✅ Judges can see the race unfold visually
- ✅ Time difference is immediately obvious
- ✅ Pit stop events are clearly marked
- ✅ Tire strategy impact is visible

## 🚀 Quick Start

**One command to see it all:**

```bash
# Terminal 1: Start backend pipeline
cd backend && python race_replay.py && python race_monitor_v2.py LEC monaco_2024

# Terminal 2: Start frontend
cd frontend && npm run dev
```

Then open http://localhost:5173 and watch the split-screen race comparison in action!

## 💡 Pro Tips

1. **Slow down replay** to watch animation more clearly:
   ```python
   # In race_replay.py, increase sleep time
   time.sleep(2)  # 2 seconds between laps instead of 1
   ```

2. **Jump to interesting lap** to show pit stop impact:
   ```python
   # In race_replay.py
   for lap_num in range(40, 78):  # Start at lap 40
   ```

3. **Test without real data** using the comparison engine directly:
   ```bash
   cd backend
   python race_comparison_engine.py
   ```

---

**This visualization transforms your hackathon demo from "here are some numbers" to "watch the AI race strategy beat the baseline in real-time!"** 🏁
