"""
FastAPI server for F1 Race Strategy System
Provides REST API endpoints for the interactive race simulator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from interactive_race_simulator import InteractiveRaceSimulator, DecisionOption
from supabase import create_client
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# Supabase connection for Arduino display
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase_client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connected for Arduino display updates")
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {e}")

app = FastAPI(title="F1 Race Strategy API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active race sessions with full state
race_sessions = {}

class RaceSessionState:
    """Track full race state like run_race_compact.py"""
    def __init__(self, simulator, total_laps):
        self.simulator = simulator
        self.total_laps = total_laps
        self.pit_plan = None
        self.first_pit_done = False
        self.second_pit_done = False
        self.pace_modifier = 0.0
        self.wear_multiplier = 1.0
        self.effective_tire_age = 0.0
        self.last_tactical_lap = 0
        self.last_pit_decision_lap = 0
        self.pit_count = 0
        self.TACTICAL_COOLDOWN = 8  # Reduced for more frequent tactical prompts
        self.PIT_DECISION_COOLDOWN = 5
        self.tactical_mode_expires_lap = None  # When to auto-revert to MAINTAIN
        self.TACTICAL_DURATION = 3  # Tactical modes last 3 laps


class RaceStartRequest(BaseModel):
    session_id: str
    race_year: int = 2024
    race_name: str = "Bahrain"
    comparison_driver: str = "VER"
    starting_position: int = 3
    starting_compound: str = "SOFT"


class DecisionRequest(BaseModel):
    session_id: str
    option_id: int


class StrategyOptionResponse(BaseModel):
    id: int
    option: str
    title: str
    description: str
    reasoning: str
    raceTimeImpact: str
    lapTimeImpact: str
    tireWear: str
    pros: List[str]
    cons: List[str]
    confidence: str


class RaceStateResponse(BaseModel):
    currentLap: int
    position: int
    tireCompound: str
    tireAge: int
    drivingStyle: str
    totalRaceTime: float
    pitStops: int
    strategies: List[StrategyOptionResponse]
    raceFinished: bool = False


# Helper function to send messages to Arduino display via Supabase
def send_to_arduino_display(message: str, message_type: str = 'STRATEGY', priority: int = 5):
    """Send a message to the Arduino display via Supabase driver_display table"""
    if not supabase_client:
        print(f"⚠️  [API→SUPABASE] Cannot send to Arduino: Supabase not connected")
        return

    try:
        print(f"\n{'='*70}")
        print(f"📤 [API→SUPABASE] Uploading message to Supabase:")
        print(f"   Type: {message_type}")
        print(f"   Message: {message}")
        print(f"   Priority: {priority}")

        result = supabase_client.table('driver_display').insert({
            'message_type': message_type,
            'content': {'message': message},
            'priority': priority,
            'acknowledged': False
        }).execute()

        msg_id = result.data[0]['id'] if result.data else 'unknown'
        print(f"✅ [API→SUPABASE] Successfully uploaded to Supabase (ID: {msg_id})")
        print(f"{'='*70}\n")
    except Exception as e:
        print(f"❌ [API→SUPABASE] Failed to upload: {e}")
        print(f"{'='*70}\n")


@app.get("/")
def root():
    return {
        "message": "F1 Race Strategy API",
        "version": "1.0",
        "endpoints": [
            "/api/races/available",
            "/api/race/start",
            "/api/race/state",
            "/api/race/decision"
        ]
    }


@app.get("/api/races/available")
def get_available_races():
    """Get list of available races from FastF1 - for race selection screen"""
    try:
        import fastf1

        # 2024 F1 Season races
        races_2024 = [
            {"id": "bahrain", "name": "Bahrain Grand Prix", "country": "Bahrain", "laps": 57},
            {"id": "saudi_arabia", "name": "Saudi Arabian Grand Prix", "country": "Saudi Arabia", "laps": 50},
            {"id": "australia", "name": "Australian Grand Prix", "country": "Australia", "laps": 58},
            {"id": "japan", "name": "Japanese Grand Prix", "country": "Japan", "laps": 53},
            {"id": "china", "name": "Chinese Grand Prix", "country": "China", "laps": 56},
            {"id": "miami", "name": "Miami Grand Prix", "country": "USA", "laps": 57},
            {"id": "imola", "name": "Emilia Romagna Grand Prix", "country": "Italy", "laps": 63},
            {"id": "monaco", "name": "Monaco Grand Prix", "country": "Monaco", "laps": 78},
            {"id": "canada", "name": "Canadian Grand Prix", "country": "Canada", "laps": 70},
            {"id": "spain", "name": "Spanish Grand Prix", "country": "Spain", "laps": 66},
            {"id": "austria", "name": "Austrian Grand Prix", "country": "Austria", "laps": 71},
            {"id": "britain", "name": "British Grand Prix", "country": "Great Britain", "laps": 52},
            {"id": "hungary", "name": "Hungarian Grand Prix", "country": "Hungary", "laps": 70},
            {"id": "belgium", "name": "Belgian Grand Prix", "country": "Belgium", "laps": 44},
            {"id": "netherlands", "name": "Dutch Grand Prix", "country": "Netherlands", "laps": 72},
            {"id": "italy", "name": "Italian Grand Prix", "country": "Italy", "laps": 53},
            {"id": "azerbaijan", "name": "Azerbaijan Grand Prix", "country": "Azerbaijan", "laps": 51},
            {"id": "singapore", "name": "Singapore Grand Prix", "country": "Singapore", "laps": 62},
            {"id": "united_states", "name": "United States Grand Prix", "country": "USA", "laps": 56},
            {"id": "mexico", "name": "Mexico City Grand Prix", "country": "Mexico", "laps": 71},
            {"id": "brazil", "name": "São Paulo Grand Prix", "country": "Brazil", "laps": 71},
            {"id": "las_vegas", "name": "Las Vegas Grand Prix", "country": "USA", "laps": 50},
            {"id": "qatar", "name": "Qatar Grand Prix", "country": "Qatar", "laps": 57},
            {"id": "abu_dhabi", "name": "Abu Dhabi Grand Prix", "country": "UAE", "laps": 58}
        ]

        # Available tire compounds
        tire_compounds = [
            {"id": "SOFT", "name": "Soft", "color": "red", "maxLaps": 25, "description": "Fastest but wears quickly"},
            {"id": "MEDIUM", "name": "Medium", "color": "yellow", "maxLaps": 40, "description": "Balanced performance"},
            {"id": "HARD", "name": "Hard", "color": "white", "maxLaps": 60, "description": "Most durable, slower pace"}
        ]

        # Starting positions (typically P1-P20)
        starting_positions = list(range(1, 21))

        # Top drivers for comparison
        comparison_drivers = [
            {"code": "VER", "name": "Max Verstappen", "team": "Red Bull Racing"},
            {"code": "PER", "name": "Sergio Perez", "team": "Red Bull Racing"},
            {"code": "LEC", "name": "Charles Leclerc", "team": "Ferrari"},
            {"code": "SAI", "name": "Carlos Sainz", "team": "Ferrari"},
            {"code": "HAM", "name": "Lewis Hamilton", "team": "Mercedes"},
            {"code": "RUS", "name": "George Russell", "team": "Mercedes"},
            {"code": "NOR", "name": "Lando Norris", "team": "McLaren"},
            {"code": "PIA", "name": "Oscar Piastri", "team": "McLaren"},
            {"code": "ALO", "name": "Fernando Alonso", "team": "Aston Martin"},
            {"code": "STR", "name": "Lance Stroll", "team": "Aston Martin"}
        ]

        return {
            "success": True,
            "data": {
                "races": races_2024,
                "tireCompounds": tire_compounds,
                "startingPositions": starting_positions,
                "comparisonDrivers": comparison_drivers,
                "defaultSettings": {
                    "race": "bahrain",
                    "position": 3,
                    "compound": "SOFT",
                    "driver": "VER"
                }
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/race/start")
def start_race(request: RaceStartRequest):
    """Start a new race simulation session - matches run_race_compact.py"""
    try:
        # Map race IDs to FastF1 race names
        race_name_map = {
            "bahrain": "Bahrain",
            "saudi_arabia": "Saudi Arabia",
            "australia": "Australia",
            "japan": "Japan",
            "china": "China",
            "miami": "Miami",
            "imola": "Emilia Romagna",
            "monaco": "Monaco",
            "canada": "Canada",
            "spain": "Spain",
            "austria": "Austria",
            "britain": "Great Britain",
            "hungary": "Hungary",
            "belgium": "Belgium",
            "netherlands": "Netherlands",
            "italy": "Italy",
            "azerbaijan": "Azerbaijan",
            "singapore": "Singapore",
            "united_states": "United States",
            "mexico": "Mexico",
            "brazil": "Brazil",
            "las_vegas": "Las Vegas",
            "qatar": "Qatar",
            "abu_dhabi": "Abu Dhabi"
        }

        # Get FastF1 race name
        fastf1_race_name = race_name_map.get(request.race_name.lower(), request.race_name)

        # Create new simulator instance - EXACTLY like run_race_compact.py
        simulator = InteractiveRaceSimulator(
            race_year=request.race_year,
            race_name=fastf1_race_name,
            total_laps=None,  # Auto-detect from data
            comparison_driver=request.comparison_driver,
            demo_mode=False
        )

        # Start the race
        race_info = simulator.start_race(
            starting_position=request.starting_position,
            starting_compound=request.starting_compound
        )

        # Create session state
        session_state = RaceSessionState(simulator, simulator.total_laps)
        race_sessions[request.session_id] = session_state

        # First decision: STYLE (lap 1)
        from driving_style import DrivingStyle
        style_options = [
            {
                'id': 1,
                'name': 'AGGRESSIVE',
                'impact': '-0.3s/lap +40%wear',
                'conf': 'RECOMMENDED',
                'style': 'AGGRESSIVE',
                'pace': -0.3,
                'wear': 1.4
            },
            {
                'id': 2,
                'name': 'BALANCED',
                'impact': 'Normal',
                'conf': 'HIGHLY_RECOMMENDED',
                'style': 'BALANCED',
                'pace': 0.0,
                'wear': 1.0
            },
            {
                'id': 3,
                'name': 'CONSERVATIVE',
                'impact': '+0.4s/lap -30%wear',
                'conf': 'ALTERNATIVE',
                'style': 'CONSERVATIVE',
                'pace': 0.4,
                'wear': 0.7
            }
        ]

        return {
            "success": True,
            "raceInfo": race_info,
            "currentLap": 1,
            "totalLaps": simulator.total_laps,  # Return actual total laps from FastF1 data
            "state": get_race_state_from_session(session_state),
            "strategies": [{
                "id": opt['id'],
                "option": f"OPTION {opt['id']}",
                "title": f"{opt['name']} Driving",
                "description": opt['impact'],
                "reasoning": f"Start with {opt['name'].lower()} style",
                "raceTimeImpact": f"{opt['pace'] * simulator.total_laps:+.1f}s",
                "lapTimeImpact": f"{opt['pace']:+.1f}s",
                "tireWear": f"{opt['wear']:.1f}x",
                "pros": [],
                "cons": [],
                "confidence": opt['conf'],
                "decisionType": "STYLE",
                "params": opt
            } for opt in style_options]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/race/state/{session_id}")
def get_state(session_id: str):
    """Get current race state"""
    if session_id not in race_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    simulator = race_sessions[session_id]
    state = simulator.state

    # Get current decision options
    options = simulator.generate_decision_options(state.current_lap)

    return {
        "currentLap": state.current_lap,
        "position": state.position,
        "tireCompound": state.tire_compound,
        "tireAge": state.tire_age,
        "drivingStyle": state.driving_style.value,
        "totalRaceTime": state.total_race_time,
        "pitStops": len(state.pit_stops),
        "strategies": convert_options_to_response(options),
        "raceFinished": state.current_lap >= simulator.total_laps
    }


@app.post("/api/race/decision")
def make_decision(request: DecisionRequest):
    """Execute decision and simulate laps until next decision - EXACTLY like run_race_compact.py"""
    if request.session_id not in race_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = race_sessions[request.session_id]
    sim = session.simulator

    # Handle the decision based on current state
    # This is the user's choice from the options presented
    decision_params = None

    # Apply the decision (STYLE, TACTICAL, or PIT)
    # We'll store this in session for next iteration
    if not hasattr(session, 'pending_decision_type'):
        # First decision is STYLE
        session.pending_decision_type = 'STYLE'

    # Apply the decision based on type
    if session.pending_decision_type == 'STYLE':
        # Apply style decision
        style_map = {1: 'AGGRESSIVE', 2: 'BALANCED', 3: 'CONSERVATIVE'}
        params_map = {
            1: {'pace': -0.3, 'wear': 1.4},
            2: {'pace': 0.0, 'wear': 1.0},
            3: {'pace': 0.4, 'wear': 0.7}
        }

        if request.option_id in params_map:
            params = params_map[request.option_id]
            session.pace_modifier = params['pace']
            session.wear_multiplier = params['wear']
            sim.tire_model.driving_style_multiplier = session.wear_multiplier

            from driving_style import DrivingStyle
            sim.state.driving_style = DrivingStyle[style_map[request.option_id]]

            # Send to Arduino display with descriptive message
            style_name = style_map[request.option_id]
            send_to_arduino_display(f"{style_name} DRIVING MODE", 'STRATEGY', priority=5)

    elif session.pending_decision_type == 'TACTICAL':
        # Apply tactical decision (PUSH, MAINTAIN, CONSERVE)
        # IMPORTANT: PUSH/CONSERVE are TEMPORARY (3 laps), then auto-revert to MAINTAIN
        tactical_map = {
            1: {'pace': -0.15, 'wear': 1.2, 'temporary': True, 'name': 'PUSH'},
            2: {'pace': 0.0, 'wear': 1.0, 'temporary': False, 'name': 'MAINTAIN'},
            3: {'pace': 0.15, 'wear': 0.8, 'temporary': True, 'name': 'CONSERVE'}
        }
        if request.option_id in tactical_map:
            params = tactical_map[request.option_id]
            session.pace_modifier = params['pace']
            session.wear_multiplier = params['wear']

            # Set expiry for temporary modes (PUSH/CONSERVE)
            current_lap = sim.state.current_lap
            if params['temporary']:
                session.tactical_mode_expires_lap = current_lap + session.TACTICAL_DURATION
                print(f"⏱️  Tactical mode active for {session.TACTICAL_DURATION} laps (expires lap {session.tactical_mode_expires_lap})")
            else:
                session.tactical_mode_expires_lap = None  # MAINTAIN has no expiry

            # Send to Arduino display with descriptive message
            tactic_name = params['name']
            if params['temporary']:
                # For PUSH/CONSERVE, show duration
                send_to_arduino_display(f"{tactic_name} FOR {session.TACTICAL_DURATION} LAPS", 'STRATEGY', priority=5)
            else:
                # For MAINTAIN
                send_to_arduino_display(f"{tactic_name} PACE", 'STRATEGY', priority=5)

    elif session.pending_decision_type == 'PIT':
        # User selected pit option - extract lap and compound from option params
        # The frontend sends option_id (1, 2, or 3) corresponding to tire compound choice
        if hasattr(session, 'last_pit_window'):
            window = session.last_pit_window

            # Map option_id to tire compound (matches generate_pit_options order)
            compound_map = {
                1: window['optimal_compound'],  # Recommended
                2: 'SOFT',  # Alternative if available
                3: 'HARD'   # Alternative
            }

            chosen_compound = compound_map.get(request.option_id, window['optimal_compound'])
            session.pit_plan = (window['optimal_lap'], chosen_compound)
            print(f"✅ Pit plan set: Lap {window['optimal_lap']} → {chosen_compound}")

            # Send to Arduino display with lap and tire info on two lines
            send_to_arduino_display(f"PIT LAP {window['optimal_lap']}|{chosen_compound} TIRES", 'STRATEGY', priority=5)

    # Now simulate laps until next decision point (EXACTLY like run_race_compact.py loop)
    from pit_window_selector import PitWindowSelector
    selector = PitWindowSelector(sim.tire_model, session.total_laps)

    # Check if we've been lapped (leader finishes before we complete 57 laps)
    leader_time = 5504.7  # VER's winning time

    for lap in range(sim.state.current_lap, session.total_laps + 1):
        # Check if leader has finished while we're still racing
        if sim.state.total_race_time > leader_time and lap < session.total_laps:
            laps_behind = session.total_laps - lap
            print(f"🏁 CHECKERED FLAG! Leader finished - you're {laps_behind} lap(s) down")
            print(f"   You completed {lap} laps (lapped by leader)")
            session.was_lapped = True
            session.laps_completed = lap
            break
        # Pit if planned
        if session.pit_plan and session.pit_plan[0] == lap:
            sim.state.tire_compound = session.pit_plan[1]
            sim.state.tire_age = 0
            session.effective_tire_age = 0.0
            sim.state.total_race_time += 25.0
            sim.state.pit_stops.append({'lap': lap, 'compound': session.pit_plan[1], 'reason': 'Planned'})
            session.pit_count += 1
            session.pit_plan = None

        # Apply tactical wear multiplier
        sim.tire_model.driving_style_multiplier = session.wear_multiplier

        # Simulate lap
        sim.simulate_lap(lap)
        sim.state.current_lap = lap + 1

        # Increment effective tire age
        session.effective_tire_age += session.wear_multiplier
        sim.state.tire_age = int(session.effective_tire_age)

        # Apply tactical pace modifier
        sim.state.total_race_time += session.pace_modifier

        # Tactical modes are now permanent - no auto-revert

        max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
        tire_pct = sim.state.tire_age / max_laps

        # Calculate live position
        sim._session = session  # Store session reference for position calculation
        position, gap_ahead, gap_behind, leader_gap = calculate_live_position(sim, lap, session)
        
        # Store position from lap 56 and maintain it through the finish
        if lap == 56:
            session.locked_position = position  # Use the calculated position, not sim.state.position
            print(f"🔒 Locking position at P{session.locked_position} for final laps")
        sim.state.position = position

        # === STRATEGY ENGINE: Gap-aware intelligent recommendations ===
        laps_remaining = session.total_laps - lap
        strategic_decision_needed = False
        context = ""
        recommended = 1  # Default to MAINTAIN

        # Only offer tactical decisions when cooldown has passed
        if (lap - session.last_tactical_lap) < session.TACTICAL_COOLDOWN:
            pass  # Skip tactical decision, cooldown active
        else:
            # Analyze race situation and recommend strategy
            # KEY: Check tire sustainability first - can we afford to PUSH?

            # Calculate if we can reach end/pit window with current tire strategy
            laps_until_pit = float('inf') if session.pit_plan is None else (session.pit_plan[0] - lap)
            laps_to_cover = min(laps_until_pit, laps_remaining)
            tire_can_sustain_push = (tire_pct < 0.5) or (laps_to_cover <= 5)  # Fresh tires or sprint distance

            # PRIORITY 1: Tire sustainability check
            # If tires are worn (>60%) and we have >10 laps to cover, recommend CONSERVE
            if tire_pct > 0.60 and laps_to_cover > 10 and not tire_can_sustain_push:
                strategic_decision_needed = True
                context = f"Tire management: {int(tire_pct*100)}% wear, {int(laps_to_cover)} laps to cover"
                recommended = 2  # CONSERVE - must preserve tires

            # PRIORITY 2: Close racing battle (within 5s) - only if tires can handle it
            elif abs(gap_ahead) < 5.0 and gap_ahead > 0:
                strategic_decision_needed = True
                context = f"Attacking: {gap_ahead:.1f}s gap to P{position-1}"
                if tire_can_sustain_push:
                    recommended = 0  # PUSH to close gap
                else:
                    recommended = 1  # MAINTAIN - can't afford tire wear

            elif gap_behind > 0 and gap_behind < 5.0:
                strategic_decision_needed = True
                context = f"Defending: P{position+1} is {gap_behind:.1f}s behind"
                if tire_can_sustain_push:
                    recommended = 0  # PUSH to defend
                else:
                    recommended = 1  # MAINTAIN - defend without destroying tires

            # PRIORITY 3: Tire crisis (>75% wear, far from pit)
            elif tire_pct > 0.75 and laps_remaining > 15 and session.pit_plan is None:
                strategic_decision_needed = True
                context = f"Tire crisis: {int(tire_pct*100)}% wear, {laps_remaining} laps left"
                recommended = 2  # CONSERVE to make it to pit window

            # PRIORITY 4: Optimal tire window approaching (65-75%)
            elif 0.65 <= tire_pct <= 0.75 and session.pit_plan is None and laps_remaining > 12:
                strategic_decision_needed = True
                context = f"Pit window: {int(tire_pct*100)}% wear - pit soon or extend?"
                recommended = 2  # CONSERVE to extend, or MAINTAIN to pit soon

            # PRIORITY 5: Fresh tires out of pit (first 5 laps on new tires)
            elif sim.state.tire_age <= 5 and len(sim.state.pit_stops) > 0 and tire_pct < 0.3:
                strategic_decision_needed = True
                context = f"Fresh tires: Lap {sim.state.tire_age} on {sim.state.tire_compound}"
                # If close to someone, PUSH; otherwise MAINTAIN
                if abs(gap_ahead) < 15.0 or gap_behind < 15.0:
                    recommended = 0  # PUSH to capitalize
                else:
                    recommended = 1  # MAINTAIN to build gap

            # PRIORITY 6: Last 5 laps - all out or manage
            elif laps_remaining <= 5:
                strategic_decision_needed = True
                context = f"Final laps: {laps_remaining} to go"
                # In final 5 laps, you can afford to PUSH even with worn tires
                if abs(gap_ahead) < 10.0 or gap_behind < 10.0:
                    recommended = 0  # PUSH - in a battle
                else:
                    recommended = 1  # MAINTAIN - cruise home

        if strategic_decision_needed and (lap - session.last_tactical_lap) >= session.TACTICAL_COOLDOWN:
            # PAUSE - present tactical decision with CONTEXT
            session.pending_decision_type = 'TACTICAL'
            session.last_tactical_lap = lap

            return {
                "success": True,
                "message": f"Lap {lap} - Strategic decision",
                "context": context,
                "currentLap": lap,
                "state": get_race_state_from_session(session),
                "strategies": generate_tactical_options(recommended, context, laps_remaining, sim.state.tire_age, sim.state.tire_compound, session.wear_multiplier, sim.tire_model, session.pit_plan, session.total_laps, lap),
                "raceFinished": False
            }

        # Check for PIT decision
        pit_opportunity = (
            tire_pct >= 0.50 and
            session.pit_plan is None and
            (session.total_laps - lap) > 10 and
            (lap - session.last_pit_decision_lap) >= session.PIT_DECISION_COOLDOWN
        )

        if pit_opportunity:
            # PAUSE - present pit decision
            session.pending_decision_type = 'PIT'
            session.last_pit_decision_lap = lap

            window = selector.generate_pit_window(lap, sim.state.tire_age, sim.state.tire_compound, session.total_laps - lap)
            session.last_pit_window = window  # Store for when user makes decision

            return {
                "success": True,
                "message": f"Lap {lap} - Pit window",
                "currentLap": lap,
                "state": get_race_state_from_session(session),
                "strategies": generate_pit_options(window, session.total_laps, lap, session.wear_multiplier, sim.tire_model),
                "raceFinished": False
            }

    # Race finished
    final_comparison = sim.get_final_comparison()
    print(f"\n🏁 API SERVER: Sending final results to frontend:")
    print(f"   Position: P{final_comparison['leaderboard_position']} / {final_comparison['total_drivers']}")
    print(f"   Leaderboard entries: {len(final_comparison['full_leaderboard'])}")
    print(f"   Winner: {final_comparison['full_leaderboard'][0]['driver']} - {final_comparison['full_leaderboard'][0]['time']:.1f}s")

    # Send race finished message to Arduino
    position = final_comparison['leaderboard_position']
    send_to_arduino_display(f"RACE FINISHED|P{position}", 'STRATEGY', priority=10)

    return {
        "success": True,
        "message": "Race finished!",
        "raceFinished": True,
        "finalResults": final_comparison,
        "strategies": [],  # No more decisions to make
        "currentLap": session.total_laps,
        "state": get_race_state_from_session(session)
    }


def calculate_live_position(sim, current_lap, session=None):
    """Calculate current race position - accounts for starting grid position"""
    starting_position = sim.state.position if current_lap < 1 else getattr(sim, 'starting_position', 3)

    if current_lap < 1:
        return starting_position, 0.0, 0.0, 0.0

    # Cap at total laps to prevent position calculation beyond race end
    total_laps = getattr(sim, 'total_laps', 57)
    calc_lap = min(current_lap, total_laps)

    # For lap 57, maintain position from lap 56
    if calc_lap >= 56 and session and hasattr(session, 'locked_position'):
        print(f"🏁 FINAL LAP: Maintaining locked position P{session.locked_position}")
        # Skip all position calculation and return the locked position
        return session.locked_position, 2.0, 2.0, (session.locked_position - 1) * 3.0

    standings = []

    # First, get all drivers and their lap counts
    driver_lap_counts = {}
    for driver in sim.race_data['DriverNumber'].unique():
        driver_laps = sim.race_data[sim.race_data['DriverNumber'] == driver]
        max_lap = driver_laps['LapNumber'].max()
        driver_lap_counts[driver] = max_lap

    # Categorize drivers by laps completed
    # On final lap (57), ONLY include drivers who completed the full race distance
    # This ensures consistency with final classification
    is_final_lap = calc_lap >= total_laps
    
    if is_final_lap:
        print(f"🏁 FINAL LAP POSITION CALC: Filtering to only include drivers who completed {total_laps} laps")
    
    excluded_count = 0
    for driver in sim.race_data['DriverNumber'].unique():
        driver_laps = sim.race_data[sim.race_data['DriverNumber'] == driver]
        driver_max_lap = driver_lap_counts[driver]
        
        # On final lap, exclude drivers who didn't complete all laps (DNF/lapped)
        if is_final_lap and driver_max_lap < total_laps:
            excluded_count += 1
            continue  # Skip this driver - they didn't finish

        # Calculate laps to compare (min of calc_lap and driver's max lap)
        compare_lap = min(calc_lap, driver_max_lap)
        laps_completed = driver_laps[driver_laps['LapNumber'] <= compare_lap]

        if len(laps_completed) > 0:
            cumulative_time = laps_completed['LapTime'].sum().total_seconds()
            # Add lap deficit penalty for lapped drivers (huge time penalty per lap behind)
            lap_deficit = max(0, calc_lap - driver_max_lap)
            time_with_penalty = cumulative_time + (lap_deficit * 120.0)  # 2 minutes per lap behind

            standings.append({
                'driver': driver,
                'time': time_with_penalty,
                'laps': driver_max_lap,
                'actual_time': cumulative_time
            })
    
    if is_final_lap:
        print(f"   Included {len(standings)} drivers, excluded {excluded_count} drivers (DNF/lapped)")

    # Calculate position accounting for grid start
    # In F1, grid positions are ~8 meters apart
    # At race pace (~90-100s laps on ~5km track), that's roughly 1.5s per grid row (2 positions)
    starting_pos = getattr(sim, 'starting_position', 3)
    GRID_SLOT_TIME = 0.75  # seconds per grid position (more realistic)

    # Starting grid offset: if you start P20, you're ~14 seconds behind P1 at the start
    # This offset fades SLOWLY - starting position matters throughout the race
    fade_factor = max(0.6, 1.0 - (calc_lap / total_laps) * 0.5)  # Fades from 1.0 to 0.6 (keeps 60% of disadvantage)
    grid_time_offset = (starting_pos - 1) * GRID_SLOT_TIME * fade_factor

    # Check if we've been lapped
    session = getattr(sim, '_session', None)
    your_laps = calc_lap
    if session and hasattr(session, 'was_lapped') and session.was_lapped:
        your_laps = getattr(session, 'laps_completed', calc_lap)

    standings.append({
        'driver': 'YOU',
        'time': sim.state.total_race_time + grid_time_offset,
        'laps': your_laps,
        'actual_time': sim.state.total_race_time
    })

    standings.sort(key=lambda x: x['time'])

    user_idx = next(i for i, s in enumerate(standings) if s['driver'] == 'YOU')
    position = user_idx + 1

    # Debug lap 57 issue
    if calc_lap >= 56:
        print(f"🔍 LAP {calc_lap} DEBUG:")
        print(f"   Your raw time: {sim.state.total_race_time:.1f}s")
        print(f"   Grid offset: {grid_time_offset:.1f}s (fade: {fade_factor:.2f})")
        print(f"   Your total: {sim.state.total_race_time + grid_time_offset:.1f}s")
        print(f"   Position: P{position}")
        # Show times of cars around you
        for i in range(max(0, user_idx-2), min(len(standings), user_idx+3)):
            driver = standings[i]['driver']
            time = standings[i]['time']
            pos = i + 1
            marker = " <-- YOU" if driver == 'YOU' else ""
            print(f"   P{pos}: {driver} - {time:.1f}s{marker}")

    # Calculate gaps (positive = behind, negative = ahead)
    # Car ahead is at user_idx - 1 (lower time = faster)
    gap_to_ahead = 0.0 if user_idx == 0 else sim.state.total_race_time - standings[user_idx - 1]['time']

    # Car behind is at user_idx + 1 (higher time = slower)
    gap_to_behind = 0.0 if user_idx == len(standings) - 1 else standings[user_idx + 1]['time'] - sim.state.total_race_time

    # Gap to leader (always positive if not leading)
    leader_gap = sim.state.total_race_time - standings[0]['time'] if user_idx > 0 else 0.0

    # Debug logging
    print(f"📊 Lap {calc_lap}: P{position} | Your time: {sim.state.total_race_time:.1f}s | Gap ahead: {gap_to_ahead:+.1f}s | Gap behind: {gap_to_behind:+.1f}s")

    return position, gap_to_ahead, gap_to_behind, leader_gap

def get_race_state_from_session(session):
    """Get race state from session with live position info"""
    sim = session.simulator
    current_lap = sim.state.current_lap - 1 if sim.state.current_lap > 0 else 0

    # Get live gaps
    position, gap_ahead, gap_behind, leader_gap = calculate_live_position(sim, current_lap)

    # Format gaps for display
    gap_ahead_str = "Leader" if gap_ahead == 0 else f"{gap_ahead:+.1f}s"
    gap_behind_str = "Last" if gap_behind == 0 else f"{gap_behind:+.1f}s"

    # Calculate tire degradation
    tire_degradation = 0.0
    if sim.tire_model and sim.state.tire_age > 0:
        tire_degradation = sim.tire_model.get_degradation_rate(
            sim.state.tire_compound, 
            sim.state.tire_age
        )

    print(f"🔍 State returned: P{position} | Gap ahead: {gap_ahead_str} | Gap behind: {gap_behind_str} | Tire deg: +{tire_degradation:.2f}s")

    return {
        "position": position,
        "gapAhead": gap_ahead_str,
        "gapBehind": gap_behind_str,
        "tireCompound": sim.state.tire_compound,
        "tireAge": sim.state.tire_age,
        "tireDegradation": tire_degradation,
        "drivingStyle": sim.state.driving_style.value,
        "totalRaceTime": sim.state.total_race_time,
        "pitStops": len(sim.state.pit_stops)
    }

def generate_tactical_options(recommended, context="", laps_remaining=20, current_tire_age=10, current_compound='MEDIUM', current_wear_multiplier=1.0, tire_model=None, pit_plan=None, total_laps=57, current_lap=1):
    """Generate tactical decision options with full race impact analysis (including pit stop costs)"""

    TACTICAL_DURATION = 3  # PUSH/CONSERVE last 3 laps

    # Tactical modifiers (pace impact, wear multiplier change)
    # PUSH and CONSERVE are TEMPORARY 3-lap bursts, MAINTAIN is permanent
    opts = [
        {'id': 1, 'name': 'PUSH (3 laps)', 'pace_delta': -0.15, 'wear_mult': 1.2, 'duration': TACTICAL_DURATION},
        {'id': 2, 'name': 'MAINTAIN', 'pace_delta': 0.0, 'wear_mult': 1.0, 'duration': laps_remaining},
        {'id': 3, 'name': 'CONSERVE (3 laps)', 'pace_delta': 0.15, 'wear_mult': 0.8, 'duration': TACTICAL_DURATION}
    ]

    strategies = []

    for i, opt in enumerate(opts):
        # Calculate tire life with this strategy
        max_tire_laps = tire_model.COMPOUND_WEAR_RATES[current_compound]['max_laps']
        effective_wear_rate = current_wear_multiplier * opt['wear_mult']

        # How many laps can we go on current tires with this strategy?
        laps_on_current_tires = int((max_tire_laps - current_tire_age) / effective_wear_rate)

        # Determine if this forces an extra pit stop
        needs_extra_pit = False
        laps_to_cover = 0

        if pit_plan is None:
            # No pit planned - need to make it to race end on current tires
            laps_to_cover = laps_remaining
            needs_extra_pit = laps_on_current_tires < laps_remaining and laps_remaining > 5
        else:
            # Pit is planned - check TWO things:
            # 1. Can we make it to the planned pit?
            laps_until_planned_pit = pit_plan[0] - current_lap

            if laps_on_current_tires < laps_until_planned_pit:
                # Can't even make planned pit - need emergency pit
                needs_extra_pit = True
                laps_to_cover = laps_remaining
            else:
                # We can make the planned pit. But will the NEXT stint last to the end?
                laps_after_planned_pit = laps_remaining - laps_until_planned_pit
                planned_compound = pit_plan[1] if pit_plan[1] else 'HARD'
                next_stint_max_laps = tire_model.COMPOUND_WEAR_RATES[planned_compound]['max_laps']
                next_stint_laps_available = int(next_stint_max_laps / effective_wear_rate)

                if next_stint_laps_available < laps_after_planned_pit and laps_after_planned_pit > 3:
                    # Next stint won't make it to the end - need ANOTHER pit
                    needs_extra_pit = True
                    laps_to_cover = laps_remaining
                else:
                    # We're good - no extra pit needed
                    laps_to_cover = laps_until_planned_pit

        # Debug logging
        if i == 0:
            print(f"🔧 Tactical calc: {opt['name']} | Tire: {current_compound} age {current_tire_age}/{max_tire_laps} | Wear mult: {effective_wear_rate:.2f}")
            print(f"   Can do {laps_on_current_tires} more laps | Need to cover {laps_to_cover} laps | Extra pit? {needs_extra_pit}")
            if pit_plan:
                print(f"   Pit plan: Lap {pit_plan[0]} → {pit_plan[1]}")

        # Calculate NET race impact (only for the duration of the tactical mode)
        duration = opt['duration']
        lap_time_savings = opt['pace_delta'] * duration  # Impact over 3 laps for PUSH/CONSERVE
        pit_stop_cost = 25.0 if needs_extra_pit else 0.0
        net_race_impact = lap_time_savings + pit_stop_cost

        # Build pros/cons based on strategy
        pros = []
        cons = []

        if 'PUSH' in opt['name']:
            if not needs_extra_pit:
                pros.append(f"Save {abs(lap_time_savings):.1f}s over {duration} laps")
                pros.append("Attack or defend for 3 laps")
                pros.append("Then auto-revert to MAINTAIN")
            else:
                cons.append(f"⚠️ Forces extra pit stop (+25s)")
                cons.append(f"NET LOSS: {net_race_impact:+.1f}s total")
            cons.append(f"Tires wear 20% faster for {duration} laps")

        elif 'MAINTAIN' in opt['name']:
            pros.append("Balanced tire management")
            pros.append(f"Current tires good for ~{laps_on_current_tires} laps")
            if not needs_extra_pit:
                pros.append("No extra pit stop needed")
            cons.append("No pace advantage")

        else:  # CONSERVE
            pros.append(f"Save ~{duration * 0.2:.1f} laps of tire life")
            pros.append(f"Preserve tires for {duration} laps")
            pros.append("Then auto-revert to MAINTAIN")
            if needs_extra_pit and laps_on_current_tires >= laps_to_cover:
                pros.append("✓ Avoids extra pit stop")
            cons.append(f"Lose {abs(lap_time_savings):.1f}s over {duration} laps")
            cons.append("May drop positions")

        # Determine confidence based on net race impact
        if needs_extra_pit:
            confidence = "NOT_RECOMMENDED"  # Forces extra pit = bad
        elif i == recommended:
            confidence = "HIGHLY_RECOMMENDED"
        elif abs(net_race_impact) < 5.0:
            confidence = "RECOMMENDED"  # Close alternative
        else:
            confidence = "ALTERNATIVE"

        strategies.append({
            "id": opt['id'],
            "option": f"OPTION {opt['id']}",
            "title": f"{opt['name']} Strategy",
            "description": f"NET: {net_race_impact:+.1f}s total race impact" if needs_extra_pit else f"{opt['pace_delta']:+.1f}s/lap",
            "reasoning": f"{context}",
            "raceTimeImpact": f"{net_race_impact:+.1f}s NET (incl. pit stops)" if needs_extra_pit else f"{lap_time_savings:+.1f}s over {laps_to_cover} laps",
            "lapTimeImpact": f"{opt['pace_delta']:+.1f}s per lap",
            "tireWear": f"{opt['wear_mult']:.1f}x wear rate",
            "pros": pros,
            "cons": cons,
            "confidence": confidence,
            "decisionType": "TACTICAL",
            "params": {'pace': opt['pace_delta'], 'wear': opt['wear_mult']}
        })

    return strategies

def generate_pit_options(window, total_laps, current_lap, wear_multiplier, tire_model):
    """Generate pit stop options with tire compound selection - MATCHES run_race_compact.py"""
    # If no optimal lap (too close to race end), return "stay out" only
    if window['optimal_lap'] is None:
        return [{
            "id": 1,
            "option": "OPTION 1",
            "title": "Stay Out - Race to Finish",
            "description": "⭐ AI Recommended: No pit stop beneficial",
            "reasoning": "Too close to race end - any pit stop would lose positions",
            "raceTimeImpact": "+0.0s",
            "lapTimeImpact": "Current tires to finish",
            "tireWear": f"Current: {window['current_state']['tire_age']} laps",
            "pros": ["No time loss", "Maintain track position"],
            "cons": ["Degraded tires"],
            "confidence": "HIGHLY_RECOMMENDED",
            "decisionType": "STAY_OUT",
            "params": {}
        }]

    laps_remaining = total_laps - window['optimal_lap']

    # Get tire capabilities adjusted for driving style
    soft_max = int(tire_model.COMPOUND_WEAR_RATES['SOFT']['max_laps'] / wear_multiplier)
    medium_max = int(tire_model.COMPOUND_WEAR_RATES['MEDIUM']['max_laps'] / wear_multiplier)
    hard_max = int(tire_model.COMPOUND_WEAR_RATES['HARD']['max_laps'] / wear_multiplier)

    # Map compound to max laps
    compound_max = {
        'SOFT': soft_max,
        'MEDIUM': medium_max,
        'HARD': hard_max
    }

    options = []

    # Option 1: Optimal lap + recommended compound
    optimal_max = compound_max.get(window['optimal_compound'], hard_max)
    options.append({
        "id": 1,
        "option": "OPTION 1",
        "title": f"Pit Lap {window['optimal_lap']} → {window['optimal_compound']}",
        "description": f"⭐ AI Recommended: {window['optimal_compound']} tires",
        "reasoning": f"Optimal window (tire {window['current_state']['tire_age']} laps, {laps_remaining} laps remaining)",
        "raceTimeImpact": "+25.0s",
        "lapTimeImpact": "Fresh tires",
        "tireWear": "Reset to 0%",
        "pros": [f"Optimal timing", f"{window['optimal_compound']} lasts ~{optimal_max} laps"],
        "cons": ["25s pit stop time"],
        "confidence": "HIGHLY_RECOMMENDED",
        "decisionType": "PIT",
        "params": {'lap': window['optimal_lap'], 'compound': window['optimal_compound']}
    })

    # Option 2: Alternative compounds
    if window['optimal_compound'] != 'SOFT' and laps_remaining <= soft_max * 0.9:
        options.append({
            "id": 2,
            "option": "OPTION 2",
            "title": f"Pit Lap {window['optimal_lap']} → SOFT",
            "description": f"Alternative: SOFT tires (faster but wears quicker)",
            "reasoning": f"Faster pace, lasts ~{soft_max} laps",
            "raceTimeImpact": "+25.0s",
            "lapTimeImpact": "Faster fresh tires",
            "tireWear": "Higher degradation",
            "pros": ["Fastest compound", "Better lap times"],
            "cons": ["Wears faster", "May need another stop"],
            "confidence": "ALTERNATIVE",
            "decisionType": "PIT",
            "params": {'lap': window['optimal_lap'], 'compound': 'SOFT'}
        })

    if window['optimal_compound'] != 'HARD':
        options.append({
            "id": len(options) + 1,
            "option": f"OPTION {len(options) + 1}",
            "title": f"Pit Lap {window['optimal_lap']} → HARD",
            "description": f"Alternative: HARD tires (slower but more durable)",
            "reasoning": f"One-stop strategy, lasts ~{hard_max} laps",
            "raceTimeImpact": "+25.0s",
            "lapTimeImpact": "Slower but durable",
            "tireWear": "Low degradation",
            "pros": ["Very durable", "One-stop possible"],
            "cons": ["Slower lap times"],
            "confidence": "RECOMMENDED" if laps_remaining > 35 else "ALTERNATIVE",
            "decisionType": "PIT",
            "params": {'lap': window['optimal_lap'], 'compound': 'HARD'}
        })

    return options

def get_race_state(simulator):
    """Helper to get race state dict"""
    return {
        "position": simulator.state.position,
        "tireCompound": simulator.state.tire_compound,
        "tireAge": simulator.state.tire_age,
        "drivingStyle": simulator.state.driving_style.value,
        "totalRaceTime": simulator.state.total_race_time,
        "pitStops": len(simulator.state.pit_stops)
    }


def convert_options_to_response(options: List[DecisionOption]) -> List[dict]:
    """Convert DecisionOption objects to API response format"""
    result = []
    for i, opt in enumerate(options, 1):
        # Map confidence to emoji prefix
        emoji = {
            'HIGHLY_RECOMMENDED': '⭐',
            'RECOMMENDED': '✅',
            'ALTERNATIVE': '🔧'
        }.get(opt.ai_confidence, '❓')

        result.append({
            "id": opt.option_id,
            "option": f"OPTION {i}",
            "title": opt.title,
            "description": opt.description,
            "reasoning": opt.reasoning,
            "raceTimeImpact": f"{opt.predicted_race_time_impact:+.1f}s",
            "lapTimeImpact": f"{opt.predicted_lap_time_impact:+.1f}s",
            "tireWear": f"{opt.tire_wear_impact:.1f}x",
            "pros": opt.pros,
            "cons": opt.cons,
            "confidence": opt.ai_confidence
        })

    return result


@app.get("/api/agents/insights/{session_id}")
def get_agent_insights(session_id: str):
    """Get real-time agent insights for dashboard"""
    if session_id not in race_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = race_sessions[session_id]
    simulator = session.simulator
    state = simulator.state
    
    # Calculate real-time insights
    avg_lap_time = state.total_race_time / max(state.current_lap, 1)
    
    # Calculate gaps (simplified - in real implementation would use competitor data)
    gap_ahead = max(0.0, (state.position - 1) * 0.5)  # Assume 0.5s gap per position
    gap_behind = max(0.0, (20 - state.position) * 0.3)  # Assume 0.3s gap behind
    
    # Determine tire degradation trend
    tire_degradation = "+0.0"
    if state.tire_age > 20:
        tire_degradation = f"+{min(2.0, (state.tire_age - 20) * 0.1):.1f}"
    elif state.tire_age > 15:
        tire_degradation = f"+{min(1.0, (state.tire_age - 15) * 0.2):.1f}"
    
    # Generate tire triggers
    tire_triggers = []
    if state.tire_age > 25:
        tire_triggers.append({"message": f"Critical tire wear ({state.tire_age} laps)", "urgency": "CRITICAL"})
    elif state.tire_age > 20:
        tire_triggers.append({"message": f"High tire wear ({state.tire_age} laps)", "urgency": "HIGH"})
    elif state.tire_age > 15:
        tire_triggers.append({"message": "Tire degradation increasing", "urgency": "MEDIUM"})
    
    # Generate position triggers
    position_triggers = []
    if gap_behind < 1.0:
        position_triggers.append({"message": "Driver behind closing gap", "urgency": "HIGH"})
    elif gap_ahead < 2.0:
        position_triggers.append({"message": "Opportunity to attack ahead", "urgency": "MEDIUM"})
    
    # Generate competitor threats
    threats = 0
    if gap_behind < 2.0:
        threats += 1
    if gap_ahead < 1.5:
        threats += 1
    
    return {
        "tire": {
            "compound": state.tire_compound,
            "tire_age": state.tire_age,
            "degradation": tire_degradation,
            "status": "active",
            "triggers": tire_triggers
        },
        "laptime": {
            "current_time": f"{avg_lap_time:.3f}",
            "avg_time": f"{avg_lap_time:.3f}",
            "trend": state.driving_style.value,
            "status": "active",
            "triggers": []
        },
        "position": {
            "position": state.position,
            "gap_ahead": f"+{gap_ahead:.1f}",
            "gap_behind": f"-{gap_behind:.1f}",
            "status": "active",
            "triggers": position_triggers
        },
        "competitor": {
            "threats": threats,
            "pit_status": f"{len(state.pit_stops)} STOPS" if state.pit_stops else "NO STOPS",
            "status": "active",
            "triggers": []
        }
    }


@app.get("/api/agents/status/{session_id}")
def get_agent_status(session_id: str):
    """Get detailed agent status for modals"""
    if session_id not in race_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = race_sessions[session_id]
    simulator = session.simulator
    state = simulator.state
    
    # Calculate detailed metrics
    avg_lap_time = state.total_race_time / max(state.current_lap, 1)
    gap_ahead = max(0.0, (state.position - 1) * 0.5)
    gap_behind = max(0.0, (20 - state.position) * 0.3)
    
    return {
        "tire": {
            "compound": state.tire_compound,
            "age": state.tire_age,
            "degradation": f"+{min(2.0, max(0, state.tire_age - 15) * 0.1):.1f}s",
            "predicted_cliff": max(0, 30 - state.tire_age),
            "status": "active"
        },
        "laptime": {
            "current_time": f"{avg_lap_time:.3f}s",
            "avg_time": f"{avg_lap_time:.3f}s",
            "trend": state.driving_style.value,
            "sector_times": {
                "sector1": f"{avg_lap_time * 0.35:.3f}s",
                "sector2": f"{avg_lap_time * 0.40:.3f}s", 
                "sector3": f"{avg_lap_time * 0.25:.3f}s"
            }
        },
        "position": {
            "position": state.position,
            "gap_ahead": f"+{gap_ahead:.1f}s",
            "gap_behind": f"-{gap_behind:.1f}s",
            "total_laps": simulator.total_laps,
            "laps_remaining": max(0, simulator.total_laps - state.current_lap)
        }
    }


if __name__ == "__main__":
    print("🏎️  Starting F1 Race Strategy API Server...")
    print("📡 API will be available at http://localhost:8000")
    print("📋 Docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
