# Product Requirements Document: F1 Multi-Agent Race Strategy System

## Executive Summary

An AI-powered F1 race strategy system featuring specialized autonomous agents that analyze live race data, run simulations, debate strategies, and communicate recommendations to both pit crew engineers (via gesture-controlled dashboard) and drivers (via Arduino display alerts).

## Problem Statement

F1 race engineers must process massive amounts of telemetry data and make split-second strategy decisions under extreme pressure during 2-hour races. Current systems:
- Generate thousands of simulation results that are difficult to interpret quickly
- Require manual analysis during time-critical moments
- Communication gaps between pit wall and driver can cause missed pit calls
- No intelligent intermediary to synthesize data into actionable recommendations

## Solution Overview

A multi-agent AI system that:
1. **Monitors** live race data autonomously across multiple domains (tires, competitors, strategy)
2. **Analyzes** using proven tire degradation models and race simulation algorithms
3. **Debates** when agents disagree on optimal strategy
4. **Communicates** through intuitive interfaces (gesture controls, visual dashboard, driver display)
5. **Learns** from engineer decisions to improve future recommendations

## Target Users

### Primary Users
- **Pit Crew Race Engineers**: Make strategy decisions during live races
- **F1 Drivers**: Execute pit strategies while racing

### Demo Audience
- Hackathon judges
- Technical evaluators
- Potential investors/sponsors

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│  Historical Race Data (FastF1 API)                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Race Replay Engine (Python)                                │
│  - Lap-by-lap data playback                                 │
│  - Configurable speed (2-5 sec/lap for demo)                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Supabase Database (Real-time data store)                   │
│  Tables:                                                     │
│  - current_lap_times                                         │
│  - pit_stops                                                 │
│  - tire_data (compound, age, degradation)                   │
│  - race_positions                                            │
│  - agent_recommendations                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────────┐   ┌────────────────────────────────────┐
│  Dashboard UI    │   │  Multi-Agent Backend (Python)      │
│  (React)         │   │                                     │
│                  │   │  Agent 1: Tire Strategist          │
│  Components:     │   │  - Tire degradation model          │
│  • Agent status  │   │  - Pit window optimization         │
│  • Race map      │   │  - Performance cliff detection     │
│  • Top 3 recs    │   │                                     │
│  • Consensus     │◄──┤  Agent 2: Competitor Tracker       │
│  • Win prob %    │   │  - Opponent lap time analysis      │
│  • Sim counter   │   │  - Counter-strategy detection      │
│                  │   │  - Track position optimization     │
└────────┬─────────┘   │                                     │
         │             │  Agent 3: Coordinator               │
         │             │  - Synthesizes agent input          │
         │             │  - Resolves conflicts               │
         │             │  - Generates unified recs           │
         │             │  - Triggers new simulations         │
         │             │                                     │
         │             │  Simulation Engine:                 │
         │             │  - Ported MATLAB degradation models │
         │             │  - Race time loss calculations      │
         │             │  - Win probability estimation       │
         │             └─────────────┬───────────────────────┘
         │                           │
         ▼                           ▼
┌──────────────────────┐    ┌────────────────────────────────┐
│  Gesture Recognition │    │  Arduino Driver Display         │
│  (MediaPipe)         │    │                                 │
│                      │    │  Hardware:                      │
│  Gestures:           │    │  - Arduino Uno/Nano             │
│  • Fist pump         │    │  - 16x2 LCD or OLED display     │
│    = Confirm         │    │  - Serial USB connection        │
│  • Swipe right       │    │                                 │
│    = Aggressive      │    │  Display Content:               │
│  • Swipe left        │    │  - "LAPS TO PIT: X"             │
│    = Conservative    │    │  - "STRATEGY: A/B"              │
│  • Point             │    │  - "PIT NOW - BOX BOX BOX"      │
│    = Drill into      │    │  - "STAY OUT"                   │
│                      │    │  - Urgent alerts (flashing)     │
└──────────────────────┘    └────────────────────────────────┘
```

## Core Features

### 1. Multi-Agent AI System

#### Agent 1: Tire Strategist
**Responsibilities:**
- Monitor tire compound, age, and degradation patterns
- Use ported MATLAB degradation model (quadratic fit)
- Predict performance cliffs
- Calculate optimal pit windows
- Alert on degradation acceleration

**Inputs:**
- Current tire age (laps)
- Tire compound (Soft/Medium/Hard)
- Lap time deltas
- Track temperature
- Historical degradation curves

**Outputs:**
- "Tire performance cliff in 3 laps - pit urgency HIGH"
- "Current tires good for 8 more laps - pit window open"
- Recommended pit lap range with confidence scores

#### Agent 2: Competitor Tracker
**Responsibilities:**
- Monitor opponent positions and lap times
- Detect pace changes (fading/improving)
- Identify counter-strategy opportunities
- Calculate undercut/overcut windows
- Track position trade-off analysis

**Inputs:**
- All driver positions and lap times
- Gap to cars ahead/behind
- Opponent tire strategies
- Recent pit stops

**Outputs:**
- "Verstappen losing 0.3s/lap - opportunity to overcut"
- "Hamilton pitting now - counter-strategy: stay out 3 laps"
- Position gain/loss predictions for pit timing options

#### Agent 3: Coordinator
**Responsibilities:**
- Collect recommendations from specialist agents
- Resolve conflicts when agents disagree
- Synthesize unified strategy with confidence scores
- Decide when to trigger new simulations
- Present top 2-3 strategies with trade-offs
- Learn from engineer decisions

**Inputs:**
- Tire Agent recommendations
- Competitor Agent recommendations
- Current race context
- Engineer historical decisions

**Outputs:**
- Unified recommendation with consensus indicator:
  - ✅ All agents agree
  - ⚠️ Split decision (2-1)
  - 🚨 Strong disagreement + urgent deadline
- Top 3 strategies ranked by win probability
- Plain English explanations
- "Strategy A: Pit lap 15, 68% win, lose track position but gain tire advantage"

### 2. Simulation Engine

**Based on ported MATLAB models from Race-Strategy-Analysis repo:**

**Tire Degradation Model:**
```python
# Quadratic model: lap_time_delta = a*lap^2 + b*lap + c
# Coefficients vary by compound and track temp
def tire_degradation(lap_num, compound, track_temp):
    # Returns seconds slower than fresh tire
    pass
```

**Pit Stop Optimization:**
```python
def optimal_pit_window(current_lap, tire_age, race_laps, opponents):
    # Calculates race time for different pit lap scenarios
    # Returns: [(pit_lap, expected_position, win_probability), ...]
    pass
```

**Race Simulation:**
- Runs 10-50 scenarios per agent request
- Variables: pit lap, tire compound choice, competitor reactions
- Outputs: Expected race time, final position, win probability

**Performance:**
- Target: <2 seconds for full simulation suite
- Display: "12,847 scenarios analyzed" (can inflate for effect)

### 3. Dashboard Interface (React)

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  F1 RACE STRATEGY SYSTEM              LAP 15/58    [Monaco] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  AGENT STATUS                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🛞 Tire Agent      │ ⚠️  Degradation accelerating      │ │
│  │                    │     Pit window: Lap 15-18          │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ 🏎️ Competitor Agent│ ✅  Verstappen fading, opportunity│ │
│  │                    │     Overcut window available       │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ 🎯 Coordinator     │ ⚠️  SPLIT DECISION (2-1)          │ │
│  │                    │     Showing top strategies...      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  TOP STRATEGIES                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🥇 Strategy A: PIT LAP 15 (AGGRESSIVE)                 │ │
│  │    Win Probability: 68%                                 │ │
│  │    Trade-off: Lose P2 temporarily, gain 8-lap tire     │ │
│  │              advantage over Verstappen                  │ │
│  │    [SELECT]                                             │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ 🥈 Strategy B: PIT LAP 18 (CONSERVATIVE)               │ │
│  │    Win Probability: 54%                                 │ │
│  │    Trade-off: Maintain track position, risk tire cliff │ │
│  │    [SELECT]                                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  RACE MAP                      SIMULATIONS: 12,847 analyzed  │
│  ┌──────────────────────────┐                               │
│  │ P1 ■ YOU        +0.0s    │  CONSENSUS: ⚠️ SPLIT           │
│  │ P2 ■ VER        +2.3s    │                                │
│  │ P3 ■ HAM        +8.1s    │  Use gestures to select:       │
│  └──────────────────────────┘  👊 Confirm  ← → Explore      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key UI Elements:**
- Real-time agent activity with status icons
- Color-coded urgency (green/yellow/red backgrounds)
- Plain English strategy explanations
- Win probability percentages
- Live race position visualization
- Simulation counter (updates in real-time)
- Gesture control instructions

**Interactions:**
- Click strategy to drill into details
- Point gesture to select agent for deep dive
- Swipe gestures to filter aggressive/conservative options
- Fist pump to lock in decision

### 4. Gesture Recognition System

**Technology:** MediaPipe Hands + TensorFlow.js

**Supported Gestures:**

| Gesture | Detection Pattern | Action |
|---------|------------------|---------|
| Fist Pump | Closed fist → raised up quickly | Confirm selected strategy |
| Swipe Right | Hand moves right across frame | Filter to aggressive strategies |
| Swipe Left | Hand moves left across frame | Filter to conservative strategies |
| Point | Index finger extended, others closed | Select specific agent/strategy |
| Open Palm | All fingers extended, held steady | Pause/review (optional) |

**Implementation:**
- Webcam feed at 30 FPS
- MediaPipe hand landmark detection
- Custom gesture classifier
- Visual feedback when gesture recognized
- Confidence threshold: 85%+

**UX Flow:**
1. Race playing, strategies displayed
2. Engineer reviews options
3. Swipes right to see aggressive Strategy A details
4. Points at Tire Agent to see reasoning
5. Fist pumps to confirm Strategy A
6. Dashboard locks in, Arduino display updates

### 5. Arduino Driver Display

**Hardware:**
- Arduino Uno or Nano
- 16x2 LCD display with I2C module (or 128x64 OLED)
- USB serial connection to backend
- Optional: Small speaker for audio alerts

**Display States:**

**State 1: Monitoring (Normal)**
```
┌──────────────────┐
│ LAP 15/58  P1    │
│ TIRES OK    +2.3 │
└──────────────────┘
```

**State 2: Pit Window Approaching**
```
┌──────────────────┐
│ LAPS TO PIT: 3   │
│ STRATEGY: A      │
└──────────────────┘
```

**State 3: Pit Window Open**
```
┌──────────────────┐
│ >>> PIT NOW <<<  │
│ BOX BOX BOX      │
└──────────────────┘
```
(Flashing/inverted display)

**State 4: Strategy Change**
```
┌──────────────────┐
│ STRATEGY UPDATE! │
│ STAY OUT - RAIN  │
└──────────────────┘
```

**State 5: Debate/Split Decision**
```
┌──────────────────┐
│ TEAM ANALYZING.. │
│ STAND BY         │
└──────────────────┘
```

**Communication Protocol:**
- Serial commands from Coordinator Agent
- Format: `CMD:VALUE\n`
- Examples:
  - `PIT_COUNTDOWN:3`
  - `STRATEGY:A`
  - `URGENT:PIT_NOW`
  - `STATUS:STAY_OUT`
- Baud rate: 9600

**Physical Setup:**
- Mounted on mockup steering wheel or standalone stand
- Positioned for easy driver glance
- Clear sight line during demo

## Data Schema (Supabase)

### Table: `lap_times`
```sql
CREATE TABLE lap_times (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  driver_number INTEGER NOT NULL,
  driver_name TEXT NOT NULL,
  lap_number INTEGER NOT NULL,
  lap_time_seconds DECIMAL(6,3),
  sector_1_time DECIMAL(5,3),
  sector_2_time DECIMAL(5,3),
  sector_3_time DECIMAL(5,3),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### Table: `tire_data`
```sql
CREATE TABLE tire_data (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  driver_number INTEGER NOT NULL,
  lap_number INTEGER NOT NULL,
  compound TEXT NOT NULL, -- SOFT, MEDIUM, HARD
  tire_age INTEGER NOT NULL, -- laps on this set
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### Table: `pit_stops`
```sql
CREATE TABLE pit_stops (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  driver_number INTEGER NOT NULL,
  lap_number INTEGER NOT NULL,
  pit_duration_seconds DECIMAL(4,2),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### Table: `race_positions`
```sql
CREATE TABLE race_positions (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  lap_number INTEGER NOT NULL,
  driver_number INTEGER NOT NULL,
  position INTEGER NOT NULL,
  gap_to_leader_seconds DECIMAL(6,3),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### Table: `agent_recommendations`
```sql
CREATE TABLE agent_recommendations (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  lap_number INTEGER NOT NULL,
  agent_name TEXT NOT NULL, -- TIRE, COMPETITOR, COORDINATOR
  recommendation_type TEXT NOT NULL, -- PIT_NOW, STAY_OUT, STRATEGY_A, etc.
  confidence_score DECIMAL(3,2), -- 0.00 to 1.00
  reasoning TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## Technology Stack

### Backend
- **Language:** Python 3.10+
- **Data Source:** FastF1 library (historical F1 data)
- **Database:** Supabase (PostgreSQL with real-time subscriptions)
- **AI Agents:** Anthropic Claude API or OpenAI GPT-4
- **Web Framework:** FastAPI (REST + WebSocket endpoints)
- **Serial Communication:** PySerial (Arduino connection)

### Frontend
- **Framework:** React 18+ with TypeScript
- **State Management:** React Context or Zustand
- **Real-time Updates:** Supabase JS client (real-time subscriptions)
- **Visualization:** Chart.js or Recharts
- **Gesture Recognition:** MediaPipe Hands (TensorFlow.js)
- **Styling:** Tailwind CSS

### Hardware
- **Arduino:** Uno or Nano
- **Display:** 16x2 LCD with I2C or 128x64 OLED
- **Connection:** USB Serial
- **Optional:** Piezo buzzer for audio alerts

### Development Tools
- **Version Control:** Git/GitHub
- **Package Management:** npm (frontend), pip (backend)
- **Environment:** Docker (optional for consistent setup)

## User Stories

### As a Pit Crew Engineer:
1. I want to see real-time agent analysis so I can understand race dynamics without manual data review
2. I want clear consensus indicators so I know when agents agree vs. disagree
3. I want plain English explanations so I can quickly understand strategy trade-offs
4. I want gesture controls so I can make decisions without typing during chaotic moments
5. I want win probability estimates so I can compare strategies objectively

### As an F1 Driver:
1. I want persistent visual alerts so I don't miss pit calls during wheel-to-wheel racing
2. I want countdown timers so I can mentally prepare for pit entry
3. I want strategy confirmations so I know the team locked in a decision
4. I want urgent alerts to stand out so I react immediately when needed

### As a Hackathon Judge:
1. I want to see AI agents working autonomously without manual prompts
2. I want to understand the real-world problem being solved
3. I want to see impressive technical integration (AI + hardware + gestures)
4. I want a clear, engaging demo that tells a story

## Success Metrics

### Functional Requirements (Must-Have)
- [ ] 3 AI agents successfully analyze race data and generate recommendations
- [ ] Supabase real-time updates flow from replay → agents → dashboard
- [ ] Dashboard displays agent status, top strategies, and win probabilities
- [ ] At least 1 gesture (fist pump) reliably triggers action
- [ ] Arduino display shows pit countdown and urgent alerts
- [ ] Full demo runs smoothly for 60-90 seconds

### Performance Requirements
- [ ] Replay script pushes data every 2-5 seconds (configurable)
- [ ] Agent analysis completes within 1-2 seconds of new data
- [ ] Dashboard updates within 500ms of agent decision
- [ ] Gesture recognition latency <300ms
- [ ] Arduino display updates within 200ms of command

### Demo Requirements
- [ ] Two-station setup: Pit wall (laptop) + Driver (Arduino display)
- [ ] Historical race selected with exciting strategy moment
- [ ] Agents demonstrate split decision scenario
- [ ] Engineer uses gesture to confirm strategy
- [ ] Driver display shows countdown → urgent alert sequence
- [ ] Smooth narrative flow with clear problem/solution story

## Risk Mitigation

### Risk 1: Agent API latency causes demo lag
**Mitigation:**
- Pre-cache agent responses for demo race
- Use streaming API responses
- Fallback to pre-scripted recommendations if API fails

### Risk 2: Gesture recognition unreliable under demo conditions
**Mitigation:**
- Optimize lighting requirements beforehand
- Backup: Click-based controls alongside gestures
- Practice gestures extensively before demo
- Lower confidence threshold if needed (70% vs 85%)

### Risk 3: Arduino serial connection issues
**Mitigation:**
- Test serial connection on demo laptop ahead of time
- Backup: Display simulated Arduino screen on laptop
- Bring spare Arduino + cables
- Use reliable USB hub (not laptop ports directly)

### Risk 4: Supabase real-time subscription drops
**Mitigation:**
- Implement reconnection logic with exponential backoff
- Fallback: Poll database every 2 seconds
- Pre-load demo race data locally as backup

### Risk 5: MATLAB model porting takes too long
**Mitigation:**
- Simplify to basic quadratic degradation model if needed
- Use FastF1's built-in tire age data as proxy
- Focus on Coordinator intelligence over simulation accuracy

## MVP vs. Full Feature Set

### Minimum Viable Product (If Pressed for Time)
- ✅ 2 agents instead of 3 (Tire + Coordinator, skip Competitor)
- ✅ 1 gesture (fist pump only)
- ✅ Arduino display (most impressive hardware element)
- ✅ Basic dashboard with agent status and top recommendation
- ✅ Simple degradation model (linear instead of quadratic)
- ✅ 30-second demo of one decision moment

### Full Feature Set (Ideal)
- ✅ 3 specialized agents with debate capability
- ✅ 3-4 gestures (fist, swipe, point)
- ✅ Arduino display with multiple states
- ✅ Polished dashboard with race map, simulation counter
- ✅ Ported MATLAB degradation models
- ✅ 60-90 second demo with full narrative arc

### Nice-to-Have (If Extra Time)
- Emergency override button (physical)
- Audio alerts from Arduino (buzzer)
- Historical decision learning (show agent adapting)
- Multiple race scenarios to choose from
- Mobile-responsive dashboard

## Timeline (3-Day Hackathon)

### Day 1: Foundation (8-10 hours)
- Hour 1-2: Set up FastF1, extract historical race data
- Hour 3-4: Design Supabase schema, set up database
- Hour 5-6: Build replay script, test data flow to Supabase
- Hour 7-8: Start basic React dashboard, display live data
- Hour 9-10: Arduino setup, basic "Hello World" serial test

### Day 2: Intelligence (8-10 hours)
- Hour 1-3: Clone MATLAB repo, port degradation model to Python
- Hour 4-6: Implement Tire Agent and Coordinator Agent logic
- Hour 7-8: Integrate agents with Supabase data feed
- Hour 9-10: Dashboard shows agent recommendations

### Day 3: Integration & Polish (8-10 hours)
- Hour 1-2: Implement MediaPipe gesture recognition
- Hour 3-4: Connect gestures to dashboard decision flow
- Hour 5-6: Program Arduino display states and serial commands
- Hour 7-8: End-to-end testing, bug fixes
- Hour 9-10: Demo rehearsal, presentation prep, final polish

## Demo Script (90 seconds)

**[0:00-0:15] Setup & Introduction**
- "F1 engineers process thousands of simulations during races but struggle to interpret them quickly"
- "We built an AI multi-agent system that autonomously monitors, analyzes, and communicates strategy"
- Show two stations: Pit wall laptop + Driver display

**[0:15-0:30] Agents Monitoring**
- Race replay starts (Monaco lap 60)
- Dashboard shows 3 agents monitoring: all green ✅
- "Our specialized agents watch tire degradation, competitors, and synthesize strategies"

**[0:30-0:50] Split Decision Scenario**
- Lap 65: Tire Agent flags degradation ⚠️
- Lap 68: Competitor Agent sees opportunity ⚠️
- Coordinator: "SPLIT DECISION - 2 agents say pit now, presenting both options"
- Dashboard shows Strategy A (68% win) vs Strategy B (54% win)
- Arduino display shows "TEAM ANALYZING..."

**[0:50-1:05] Gesture Decision**
- Engineer reviews options
- "I trust the tire data" - Fist pump gesture to confirm Strategy A
- Dashboard locks in decision ✅
- Arduino display updates: "LAPS TO PIT: 2"

**[1:05-1:20] Driver Alert**
- Countdown: "LAPS TO PIT: 1"
- Arduino flashes: ">>> PIT NOW <<< BOX BOX BOX"
- Teammate at driver station: "Pitting!"

**[1:20-1:30] Outcome**
- Race outcome: Strategy works, P1 finish
- "Our system bridges HPC simulations with intuitive human interfaces"
- "Gesture controls + AI agents + driver alerts = faster, better decisions"

## Open Questions

1. **Which Claude/GPT model for agents?** Claude 3.5 Sonnet vs GPT-4 Turbo
   - Trade-off: Cost vs. response quality
   - Recommendation: Claude Sonnet (better reasoning for strategy)

2. **Historical race selection?**
   - Candidates: Monaco 2024 (Piastri vs Leclerc), Singapore 2023 (Sainz strategy)
   - Criteria: Clear strategy fork, exciting outcome, <20 lap demo window

3. **Team roles?**
   - Person 1: Backend (agents, replay, Supabase)
   - Person 2: Frontend (React dashboard, gestures)
   - Person 3: Hardware (Arduino) + Integration
   - Person 4: Demo polish + presentation

4. **Backup plan if gesture recognition fails?**
   - Mouse/keyboard controls
   - Pre-recorded gesture video
   - Focus demo on agents + Arduino instead

## Appendix A: Ported MATLAB Models

### Tire Degradation Model
```python
import numpy as np

# Coefficients from Safety_Car_Window_Calculations.m
TIRE_COEFFICIENTS = {
    'SOFT': {'a': 0.008, 'b': 0.02, 'c': 0.0},    # Degrades quickly
    'MEDIUM': {'a': 0.004, 'b': 0.015, 'c': 0.0}, # Moderate degradation
    'HARD': {'a': 0.002, 'b': 0.01, 'c': 0.0}     # Degrades slowly
}

def tire_degradation_delta(lap_number: int, compound: str, track_temp: float = 30.0) -> float:
    """
    Calculate lap time delta due to tire degradation.

    Args:
        lap_number: Number of laps on current tire set
        compound: 'SOFT', 'MEDIUM', or 'HARD'
        track_temp: Track temperature in Celsius (affects degradation rate)

    Returns:
        Seconds slower than fresh tire
    """
    coef = TIRE_COEFFICIENTS[compound]

    # Temperature adjustment (higher temp = faster degradation)
    temp_factor = 1.0 + (track_temp - 30) / 100

    # Quadratic degradation model
    delta = (coef['a'] * lap_number**2 + coef['b'] * lap_number + coef['c']) * temp_factor

    return delta

def predict_cliff_lap(compound: str, threshold: float = 2.0) -> int:
    """
    Predict which lap tire performance falls off cliff.

    Args:
        compound: Tire compound
        threshold: Delta threshold for "cliff" (seconds)

    Returns:
        Lap number where degradation exceeds threshold
    """
    for lap in range(1, 50):
        if tire_degradation_delta(lap, compound) > threshold:
            return lap
    return 50  # Max stint length
```

### Pit Stop Optimization
```python
def optimal_pit_window(
    current_lap: int,
    tire_age: int,
    total_race_laps: int,
    compound: str,
    pit_loss_time: float = 25.0
) -> list[tuple[int, float]]:
    """
    Calculate optimal pit window based on tire degradation.

    Args:
        current_lap: Current lap number
        tire_age: Laps on current tires
        total_race_laps: Total race distance
        compound: Current tire compound
        pit_loss_time: Time lost in pit (seconds)

    Returns:
        List of (pit_lap, expected_race_time) tuples
    """
    scenarios = []

    for pit_lap in range(current_lap, total_race_laps - 5):
        # Calculate race time for this pit strategy
        race_time = 0.0

        # Time on current tires until pit
        for lap in range(current_lap, pit_lap):
            age = tire_age + (lap - current_lap)
            race_time += 90.0 + tire_degradation_delta(age, compound)  # 90s base lap

        # Pit stop time
        race_time += pit_loss_time

        # Time on fresh tires after pit
        for lap in range(pit_lap, total_race_laps):
            new_age = lap - pit_lap
            race_time += 90.0 + tire_degradation_delta(new_age, compound)

        scenarios.append((pit_lap, race_time))

    # Sort by race time (lowest first)
    scenarios.sort(key=lambda x: x[1])

    return scenarios[:5]  # Return top 5 strategies
```

## Appendix B: Agent System Prompts

### Tire Agent Prompt
```
You are the Tire Strategist agent for an F1 team. Your sole responsibility is analyzing tire performance and degradation.

You will receive:
- Current tire compound (SOFT/MEDIUM/HARD)
- Tire age in laps
- Recent lap times
- Track temperature

Your tasks:
1. Analyze tire degradation rate using the quadratic model
2. Predict when performance will fall off a "cliff"
3. Recommend optimal pit window (lap range)
4. Assess urgency (LOW/MEDIUM/HIGH/CRITICAL)

Output format:
{
  "status": "OK" | "WARNING" | "CRITICAL",
  "recommendation": "PIT_NOW" | "PIT_SOON" | "TIRES_OK",
  "pit_window": [15, 18],
  "reasoning": "Tire degradation accelerating. Current delta: 1.2s. Cliff predicted lap 17. Pit window: laps 15-18.",
  "urgency": "HIGH",
  "confidence": 0.85
}

Be concise. Speak in race engineer language. Focus only on tire performance.
```

### Competitor Agent Prompt
```
You are the Competitor Tracker agent for an F1 team. You monitor opponents and identify strategic opportunities.

You will receive:
- All driver positions and lap times
- Recent pit stops
- Gap to cars ahead/behind

Your tasks:
1. Detect opponent pace changes (improving/fading)
2. Identify undercut/overcut opportunities
3. Predict competitor pit strategies
4. Assess position gain/loss for different strategies

Output format:
{
  "status": "OK" | "OPPORTUNITY" | "THREAT",
  "recommendation": "COUNTER_STRATEGY" | "UNDERCUT" | "OVERCUT" | "STAY_OUT",
  "target_driver": "VER",
  "reasoning": "Verstappen losing 0.3s/lap on old tires. Undercut window open if we pit lap 15.",
  "position_impact": "Pit now: temporary P3, regain P1 by lap 20",
  "confidence": 0.78
}

Be tactical. Think like a race strategist. Focus on competitive advantage.
```

### Coordinator Agent Prompt
```
You are the Coordinator agent. You synthesize inputs from the Tire Agent and Competitor Agent to make final strategy recommendations.

You will receive:
- Tire Agent recommendation
- Competitor Agent recommendation
- Current race state

Your tasks:
1. Identify if agents agree or disagree
2. Resolve conflicts by weighing confidence scores and race context
3. Present top 2-3 strategies with trade-offs
4. Calculate win probabilities (estimated)
5. Provide clear, actionable recommendation

Output format:
{
  "consensus": "UNANIMOUS" | "SPLIT" | "CONFLICT",
  "top_strategies": [
    {
      "id": "A",
      "name": "PIT LAP 15 (AGGRESSIVE)",
      "win_probability": 0.68,
      "trade_off": "Lose track position temporarily, gain 8-lap tire advantage",
      "supporting_agents": ["TIRE", "COMPETITOR"]
    },
    {
      "id": "B",
      "name": "PIT LAP 18 (CONSERVATIVE)",
      "win_probability": 0.54,
      "trade_off": "Maintain position, risk tire cliff",
      "supporting_agents": ["COMPETITOR"]
    }
  ],
  "recommended_strategy": "A",
  "reasoning": "Tire Agent flags imminent degradation cliff (HIGH confidence). Competitor Agent sees undercut window. Aggressive pit maximizes win probability despite temporary position loss."
}

Speak in plain English. Make the complex simple. Help humans decide under pressure.
```

## Appendix C: References

- FastF1 Documentation: https://theoehrly.github.io/Fast-F1/
- Race-Strategy-Analysis GitHub: https://github.com/TomWebster98/Race-Strategy-Analysis
- MediaPipe Hands: https://google.github.io/mediapipe/solutions/hands.html
- Supabase Real-time: https://supabase.com/docs/guides/realtime
- Arduino LCD Tutorial: https://www.arduino.cc/en/Tutorial/HelloWorld

---

**Document Version:** 1.0
**Last Updated:** 2025-10-18
**Status:** Planning Phase
