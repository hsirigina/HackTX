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

# Store active race sessions
race_sessions = {}


class RaceStartRequest(BaseModel):
    session_id: str
    race_year: int = 2024
    race_name: str = "Bahrain"
    total_laps: int = 57
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
        "endpoints": ["/api/race/start", "/api/race/state", "/api/race/decision"]
    }


@app.post("/api/race/start")
def start_race(request: RaceStartRequest):
    """Start a new race simulation session"""
    try:
        # Create new simulator instance
        simulator = InteractiveRaceSimulator(
            race_year=request.race_year,
            race_name=request.race_name,
            total_laps=request.total_laps,
            comparison_driver='VER'
        )

        # Start the race
        race_info = simulator.start_race(
            starting_position=request.starting_position,
            starting_compound=request.starting_compound
        )

        # Store session
        race_sessions[request.session_id] = simulator

        # Get first decision (lap 1)
        options = simulator.generate_decision_options(1)

        return {
            "success": True,
            "raceInfo": race_info,
            "currentLap": 1,
            "state": get_race_state(simulator),
            "strategies": convert_options_to_response(options)
        }

    except Exception as e:
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
    """Execute a strategic decision"""
    if request.session_id not in race_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    simulator = race_sessions[request.session_id]

    # Get current options
    current_lap = simulator.state.current_lap
    options = simulator.generate_decision_options(current_lap)

    # Find selected option
    selected = None
    for opt in options:
        if opt.option_id == request.option_id:
            selected = opt
            break

    if not selected:
        raise HTTPException(status_code=400, detail="Invalid option_id")

    # Execute decision
    result = simulator.execute_decision(selected)

    # Simulate laps to next decision point
    next_decision_lap = get_next_decision_lap(current_lap, simulator.decision_laps)

    if next_decision_lap and next_decision_lap < simulator.total_laps:
        # Fast forward to next decision
        while simulator.state.current_lap < next_decision_lap:
            simulator.simulate_lap(simulator.state.current_lap)
            simulator.state.current_lap += 1

        # Get new options
        new_options = simulator.generate_decision_options(next_decision_lap)

        return {
            "success": True,
            "message": result['message'],
            "currentLap": next_decision_lap,
            "state": get_race_state(simulator),
            "strategies": convert_options_to_response(new_options),
            "raceFinished": False
        }
    else:
        # Race is finished or no more decisions
        # Simulate to end
        while simulator.state.current_lap < simulator.total_laps:
            simulator.simulate_lap(simulator.state.current_lap)
            simulator.state.current_lap += 1

        final_comparison = simulator.get_final_comparison()

        return {
            "success": True,
            "message": "Race finished!",
            "raceFinished": True,
            "finalResults": final_comparison
        }


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


def get_next_decision_lap(current_lap: int, decision_laps: List[int]) -> Optional[int]:
    """Find next decision lap after current lap"""
    for lap in decision_laps:
        if lap > current_lap:
            return lap
    return None


if __name__ == "__main__":
    print("🏎️  Starting F1 Race Strategy API Server...")
    print("📡 API will be available at http://localhost:8000")
    print("📋 Docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
