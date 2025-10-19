# Frontend Dashboard - Setup Complete ✅

## What Was Built

A React dashboard that displays real-time F1 race strategy AI recommendations.

### Tech Stack:
- **React 18** with **Vite** (fast build tool)
- **TailwindCSS** for styling
- **Supabase JS Client** for database access
- **Polling architecture** (every 2 seconds, as requested)

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AgentStatus.jsx      # Shows 4 data agents + coordinator status
│   │   ├── StrategyCard.jsx     # AI recommendation display
│   │   └── RacePosition.jsx     # Race position tracker
│   ├── App.jsx                  # Main app with 2s polling
│   ├── supabaseClient.js        # Supabase config
│   └── index.css                # TailwindCSS styles
├── .env                         # Supabase credentials
├── tailwind.config.js           # Tailwind config
├── package.json                 # Dependencies
└── README.md                    # Setup instructions
```

## Features Implemented

### 1. Real-Time Data Polling (Every 2 Seconds)
- Fetches latest lap data from Supabase
- Gets tire, position, and recommendation data
- Updates UI automatically

### 2. Agent Status Cards
**Displays status for:**
- 🛞 **Tire Agent** - Compound, age, degradation status
- ⏱️ **Pace Agent** - Lap times, pace analysis
- 🏁 **Position Agent** - Race position, gaps
- 🎯 **AI Coordinator** - Overall system status

**Color-coded urgency:**
- 🔴 CRITICAL (age > 30 laps, slow pace)
- 🟡 WARNING (age > 20 laps, moderate pace)
- 🟢 OK (fresh tires, good pace)

### 3. Strategy Recommendation Card
**Shows:**
- Recommendation type (PIT_NOW, STAY_OUT, PUSH, etc.)
- Urgency level (CRITICAL/HIGH/MEDIUM/LOW)
- Confidence percentage
- Pit window (if applicable)
- Target tire compound
- Team radio message for driver
- Pit crew instructions
- AI reasoning
- Key events detected
- Consensus indicator

**Visual effects:**
- Pulsing animation for CRITICAL recommendations
- F1-themed color gradients
- Large, readable fonts for quick scanning

### 4. Race Position Tracker
- Shows current position (highlighted)
- Displays nearby competitors (P±1)
- Gap timings
- Competitor agent monitoring status

### 5. Professional F1 Styling
- Dark theme with racing gradients
- Ferrari red accents
- Large, bold fonts for quick readability
- Responsive layout (desktop & mobile)

## Running the Dashboard

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

Dashboard will be available at: **http://localhost:5173**

### 3. Run with Backend Demo
In another terminal:
```bash
cd backend
source venv/bin/activate
python demo_v2.py
```

Watch the dashboard update in real-time as the race progresses!

## Data Flow

```
Backend Race Replay
       ↓
  Supabase DB
  (lap_times, tire_data, race_positions, agent_recommendations)
       ↓ (poll every 2s)
  Frontend App.jsx
       ↓ (React props)
  ┌────┴────┬─────────────┐
  │         │             │
Agent    Strategy     Position
Status    Card         Tracker
```

## Configuration

### Environment Variables (.env)
```bash
VITE_SUPABASE_URL=https://wkcdbbmelonvmduxkkge.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
```

### Demo Settings (App.jsx)
```javascript
const RACE_ID = 'monaco_2024'  // Change race
const DRIVER = 'LEC'            // Change driver
```

## Screenshots Preview

**Header:**
- Large "F1 AI Race Strategy System" title
- Monaco 2024 subtitle
- Current lap counter (e.g., "65/78")

**Left Column (Agent Status):**
- 4 color-coded agent cards
- Real-time tire age, compound, lap times
- Position and gap information

**Right Column (Strategy Card):**
- Large recommendation badge (e.g., "🏁 PIT NOW")
- Urgency and confidence meters
- Team radio messages in quotes
- AI reasoning paragraph
- Key events bullet list

**Footer:**
- "Powered by 4 Data Agents + AI Coordinator"
- Last analysis lap indicator

## Polling Implementation

As requested, the dashboard uses **polling instead of Supabase subscriptions**:

```javascript
useEffect(() => {
  const fetchData = async () => {
    // Fetch from Supabase tables
    // Update state
  }

  fetchData()  // Initial fetch
  const interval = setInterval(fetchData, 2000)  // Poll every 2s

  return () => clearInterval(interval)  // Cleanup
}, [])
```

**Benefits:**
- Simple implementation
- No WebSocket issues
- Predictable behavior
- Easy to debug

**Performance:**
- ~30 queries/minute (very light)
- Supabase easily handles this load
- Max 2-second delay (imperceptible)

## Next Steps (Optional)

The dashboard is **fully functional** and ready for demo. Optional enhancements:

1. **Gesture Recognition** - Add MediaPipe hand tracking (as in original PRD)
2. **Historical Lap Chart** - Graph lap times over race
3. **Multiple Driver View** - Toggle between drivers
4. **Sound Alerts** - Audio for CRITICAL recommendations
5. **Fullscreen Mode** - For pit wall display

## Testing

### Manual Test
1. Start backend: `python demo_v2.py`
2. Start frontend: `npm run dev`
3. Open http://localhost:5173
4. Watch dashboard update every 2 seconds

### Expected Behavior
- Current lap increments
- Agent status cards update colors
- Strategy card shows new recommendations when AI triggers
- Loading spinner on initial load
- Smooth transitions between states

## Troubleshooting

### Dashboard shows "Loading..."
- Check `.env` file has correct Supabase credentials
- Ensure backend has written data to Supabase
- Check browser console for errors

### No recommendations showing
- Backend may not have triggered AI yet
- Check Supabase `agent_recommendations` table has data
- Ensure `RACE_ID` and `DRIVER` match backend

### Styling looks broken
- Run `npm install` to ensure TailwindCSS is installed
- Check `tailwind.config.js` exists
- Verify `index.css` has Tailwind directives

## Summary

✅ **React dashboard complete**
✅ **Polling every 2 seconds** (as requested)
✅ **Agent status cards** with color-coded urgency
✅ **Strategy recommendations** with full AI context
✅ **Race position tracker**
✅ **F1-themed professional styling**
✅ **Ready for demo**

The frontend is production-ready and integrates seamlessly with the V2 backend architecture (4 Data Agents + AI Coordinator).
