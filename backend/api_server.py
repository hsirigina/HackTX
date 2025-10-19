"""
FastAPI server for F1 Race Strategy System
Provides REST API endpoints for the interactive race simulator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from interactive_race_simulator import InteractiveRaceSimulator, DecisionOption
import uvicorn

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
        self.TACTICAL_COOLDOWN = 10
        self.PIT_DECISION_COOLDOWN = 5


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

    elif session.pending_decision_type == 'TACTICAL':
        # Apply tactical decision (PUSH, MAINTAIN, CONSERVE)
        tactical_map = {
            1: {'pace': -0.2, 'wear': 0.2},
            2: {'pace': 0.0, 'wear': 0.0},
            3: {'pace': 0.2, 'wear': -0.2}
        }
        if request.option_id in tactical_map:
            params = tactical_map[request.option_id]
            session.pace_modifier += params['pace']
            session.wear_multiplier += params['wear']

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

    # Now simulate laps until next decision point (EXACTLY like run_race_compact.py loop)
    from pit_window_selector import PitWindowSelector
    selector = PitWindowSelector(sim.tire_model, session.total_laps)

    for lap in range(sim.state.current_lap, session.total_laps + 1):
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

        max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
        tire_pct = sim.state.tire_age / max_laps

        # Calculate live position
        position, gap_ahead, gap_behind, leader_gap = calculate_live_position(sim, lap)
        sim.state.position = position

        # Check for TACTICAL decision
        tactical_opportunity = (
            abs(gap_ahead) < 3.0 or
            gap_behind < 2.0 or
            (position <= 3 and abs(leader_gap) < 10.0)
        )

        if tactical_opportunity and (lap - session.last_tactical_lap) >= session.TACTICAL_COOLDOWN:
            # PAUSE - present tactical decision with CONTEXT
            session.pending_decision_type = 'TACTICAL'
            session.last_tactical_lap = lap

            # Determine context and recommendation (EXACTLY like run_race_compact.py)
            if abs(gap_ahead) < 3.0:
                context = f"Close gap: {abs(gap_ahead):.1f}s ahead"
                recommended = 0  # PUSH
            elif gap_behind < 2.0:
                context = f"Under pressure: {gap_behind:.1f}s behind"
                recommended = 0  # PUSH
            else:
                context = f"P{position} - Managing position"
                recommended = 1  # MAINTAIN

            return {
                "success": True,
                "message": f"Lap {lap} - Tactical decision",
                "context": context,  # Add context for frontend
                "currentLap": lap,
                "state": get_race_state_from_session(session),
                "strategies": generate_tactical_options(recommended, context),
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
    return {
        "success": True,
        "message": "Race finished!",
        "raceFinished": True,
        "finalResults": final_comparison,
        "currentLap": session.total_laps,
        "state": get_race_state_from_session(session)
    }


def calculate_live_position(sim, current_lap):
    """Calculate current race position - COPIED from run_race_compact.py"""
    if current_lap < 1:
        return 3, 0.0, 0.0, 0.0

    standings = []
    for driver in sim.race_data['DriverNumber'].unique():
        driver_laps = sim.race_data[sim.race_data['DriverNumber'] == driver]
        laps_completed = driver_laps[driver_laps['LapNumber'] <= current_lap]

        if len(laps_completed) > 0:
            cumulative_time = laps_completed['LapTime'].sum().total_seconds()
            standings.append({
                'driver': driver,
                'time': cumulative_time
            })

    standings.append({
        'driver': 'YOU',
        'time': sim.state.total_race_time
    })

    standings.sort(key=lambda x: x['time'])

    user_idx = next(i for i, s in enumerate(standings) if s['driver'] == 'YOU')
    position = user_idx + 1

    gap_to_ahead = 0.0 if user_idx == 0 else sim.state.total_race_time - standings[user_idx - 1]['time']
    gap_to_behind = 0.0 if user_idx == len(standings) - 1 else standings[user_idx + 1]['time'] - sim.state.total_race_time
    leader_gap = sim.state.total_race_time - standings[0]['time'] if user_idx > 0 else 0.0

    return position, gap_to_ahead, gap_to_behind, leader_gap

def get_race_state_from_session(session):
    """Get race state from session"""
    return {
        "position": session.simulator.state.position,
        "tireCompound": session.simulator.state.tire_compound,
        "tireAge": session.simulator.state.tire_age,
        "drivingStyle": session.simulator.state.driving_style.value,
        "totalRaceTime": session.simulator.state.total_race_time,
        "pitStops": len(session.simulator.state.pit_stops)
    }

def generate_tactical_options(recommended, context=""):
    """Generate tactical decision options with context - MATCHES run_race_compact.py"""
    opts = [
        {'id': 1, 'name': 'PUSH', 'impact': '-0.2s/lap +20%wear', 'pace': -0.2, 'wear': 0.2},
        {'id': 2, 'name': 'MAINTAIN', 'impact': 'No change', 'pace': 0.0, 'wear': 0.0},
        {'id': 3, 'name': 'CONSERVE', 'impact': '+0.2s/lap -20%wear', 'pace': 0.2, 'wear': -0.2}
    ]

    return [{
        "id": opt['id'],
        "option": f"OPTION {opt['id']}",
        "title": opt['name'],
        "description": opt['impact'],
        "reasoning": f"{context} - {opt['name']} pace strategy",
        "raceTimeImpact": f"{opt['pace'] * 20:+.1f}s over 20 laps",
        "lapTimeImpact": f"{opt['pace']:+.1f}s",
        "tireWear": f"{1.0 + opt['wear']:.1f}x",
        "pros": [],
        "cons": [],
        "confidence": "HIGHLY_RECOMMENDED" if i == recommended else ("RECOMMENDED" if i == 1 else "ALTERNATIVE"),
        "decisionType": "TACTICAL",
        "params": opt
    } for i, opt in enumerate(opts)]

def generate_pit_options(window, total_laps, current_lap, wear_multiplier, tire_model):
    """Generate pit stop options with tire compound selection - MATCHES run_race_compact.py"""
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


if __name__ == "__main__":
    print("🏎️  Starting F1 Race Strategy API Server...")
    print("📡 API will be available at http://localhost:8000")
    print("📋 Docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
