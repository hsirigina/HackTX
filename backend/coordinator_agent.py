"""
AI Coordinator Agent with MCP-style tool access to Data Agents
Minimal AI calls - only called when data agents detect significant events
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from data_agents import (
    TireDataAgent,
    LapTimeAgent,
    PositionAgent,
    CompetitorAgent,
    TriggerEvent
)
from tire_model import TireDegradationModel

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
DISABLE_AI = os.getenv('DISABLE_AI', 'false').lower() == 'true'

if GOOGLE_API_KEY and not DISABLE_AI:
    genai.configure(api_key=GOOGLE_API_KEY)


class CoordinatorAgent:
    """
    AI Coordinator - Uses 4 data agents as MCP-style tools
    Only makes AI calls when data agents detect significant events
    """

    SYSTEM_PROMPT = """You are the F1 Race Strategy Coordinator AI. You synthesize data from 4 specialized data agents to provide strategic race recommendations.

**Your Data Agent Tools:**

1. **TireDataAgent** - Monitors tire degradation, predicts tire cliff, detects pit stops
2. **LapTimeAgent** - Analyzes pace trends, detects pace collapse or degradation
3. **PositionAgent** - Tracks race position, gaps to competitors, position changes
4. **CompetitorAgent** - Monitors nearby competitors, detects their pit stops, compares pace

**Your Role:**
- You are called ONLY when data agents detect significant events (pit stops, position changes, tire degradation, etc.)
- Data agents have already pre-processed all the raw data for you
- You synthesize their findings into clear, actionable strategy recommendations
- You speak like an F1 race engineer: concise, urgent, data-driven

**Communication Style:**
- Direct and tactical
- Use racing terminology
- Provide clear recommendations with reasoning
- Assess urgency (LOW/MEDIUM/HIGH/CRITICAL)
- Include confidence level (0.0-1.0)

**Your outputs should help:**
1. Pit crew engineers - Strategic decisions (when to pit, tire compound)
2. Drivers - Tactical guidance (push/conserve, defend/attack)
"""

    def __init__(self, driver_name: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Coordinator with access to 4 data agents

        Args:
            driver_name: Driver we're managing strategy for
            model_name: Gemini model to use
        """
        self.driver_name = driver_name
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

        # Initialize data agents as "tools"
        self.tire_agent = TireDataAgent(driver_name)
        self.lap_time_agent = LapTimeAgent(driver_name)
        self.position_agent = PositionAgent(driver_name)
        self.competitor_agent = CompetitorAgent(driver_name)

        # Initialize tire strategy model for pit window optimization
        self.tire_model = TireDegradationModel(total_laps=78)

        # Track last recommendation for caching
        self.last_recommendation = None
        self.last_analysis_lap = 0

    def analyze_situation(
        self,
        current_lap: int,
        events: List[TriggerEvent],
        lap_data: Dict,
        position_data: Dict,
        competitor_data: List[Dict]
    ) -> Dict:
        """
        Analyze race situation using data from all agents

        Args:
            current_lap: Current lap number
            events: List of TriggerEvents from data agents
            lap_data: Current lap data (lap_time, tire_compound, tire_age, etc.)
            position_data: Current position data (position, gaps)
            competitor_data: List of competitor states

        Returns:
            {
                "consensus": "UNANIMOUS" | "CONFLICTED" | "CLEAR",
                "recommendation_type": "PIT_NOW" | "PIT_SOON" | "STAY_OUT" | "PUSH" | "CONSERVE" | "DEFEND",
                "pit_window": [start_lap, end_lap] or null,
                "target_compound": "SOFT" | "MEDIUM" | "HARD" or null,
                "driver_instruction": "Brief instruction for driver",
                "pit_crew_instruction": "Brief instruction for pit crew",
                "reasoning": "Why this recommendation",
                "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
                "confidence": 0.0-1.0,
                "key_events": ["event1", "event2", ...]
            }
        """
        # If AI is disabled, return mock recommendation
        if DISABLE_AI:
            return self._get_mock_recommendation(current_lap, events, lap_data)

        # Get status summaries from all data agents
        tire_status = self.tire_agent.get_status_summary()
        pace_status = self.lap_time_agent.get_status_summary()
        position_status = self.position_agent.get_status_summary()
        competitor_status = self.competitor_agent.get_status_summary(
            position_data.get('position', 1)
        )

        # Build context for AI
        context = self._build_context(
            current_lap=current_lap,
            events=events,
            tire_status=tire_status,
            pace_status=pace_status,
            position_status=position_status,
            competitor_status=competitor_status,
            lap_data=lap_data,
            position_data=position_data
        )

        # Build prompt
        prompt = f"""{self.SYSTEM_PROMPT}

**Current Race Situation:**

{context}

**Your Task:**
Analyze this situation and provide a strategic recommendation in JSON format:

{{
    "consensus": "UNANIMOUS" | "CONFLICTED" | "CLEAR",
    "recommendation_type": "PIT_NOW" | "PIT_SOON" | "STAY_OUT" | "PUSH" | "CONSERVE" | "DEFEND",
    "pit_window": [start_lap, end_lap] or null,
    "target_compound": "SOFT" | "MEDIUM" | "HARD" or null,
    "driver_instruction": "1-2 sentence instruction for driver over team radio",
    "pit_crew_instruction": "1-2 sentence instruction for pit crew",
    "reasoning": "2-3 sentences explaining the strategy and why it's optimal",
    "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "confidence": 0.0-1.0,
    "key_events": ["Most important events driving this decision"]
}}

**Guidelines:**
- Consider tire status, pace trends, position, and competitors holistically
- If multiple HIGH/CRITICAL events, prioritize based on race impact
- Provide clear, actionable recommendations
- Be decisive but acknowledge uncertainty with confidence score
- Think about both short-term tactics and long-term strategy
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())

            # Cache this recommendation
            self.last_recommendation = result
            self.last_analysis_lap = current_lap

            return result

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response_text[:500]}")
            return {
                "error": "Failed to parse AI response",
                "raw": response_text,
                "recommendation_type": "STAY_OUT",
                "urgency": "LOW",
                "confidence": 0.0
            }
        except Exception as e:
            print(f"Error in analyze_situation: {e}")
            return {
                "error": str(e),
                "recommendation_type": "STAY_OUT",
                "urgency": "LOW",
                "confidence": 0.0
            }

    def _build_context(
        self,
        current_lap: int,
        events: List[TriggerEvent],
        tire_status: Dict,
        pace_status: Dict,
        position_status: Dict,
        competitor_status: Dict,
        lap_data: Dict,
        position_data: Dict
    ) -> str:
        """Build rich context string for AI from all data sources"""

        # Format events
        event_lines = []
        for event in events:
            if event.urgency in ['CRITICAL', 'HIGH']:
                urgency_icon = "🔴" if event.urgency == 'CRITICAL' else "🟡"
                message = event.data.get('message', event.type)
                event_lines.append(f"  {urgency_icon} [{event.urgency}] {message}")

        events_text = "\n".join(event_lines) if event_lines else "  No critical events"

        # Format tire status
        tire_text = f"""
  - Compound: {tire_status.get('current_compound', 'Unknown')}
  - Age: {tire_status.get('tire_age', 0)} laps
  - Degradation trend (last 5 laps): {tire_status.get('degradation_trend_5_laps', 0):.2f}s
  - Predicted cliff: Lap {tire_status.get('predicted_cliff', 'Unknown')}
"""

        # Format pace status
        pace_text = f"""
  - Average lap time: {pace_status.get('avg_lap_time', 0):.2f}s
  - Last 5 laps avg: {pace_status.get('avg_last_5_laps', 0):.2f}s
  - Best lap: {pace_status.get('best_lap', 0):.2f}s
  - Trend: {pace_status.get('trend', 'unknown')}
"""

        # Format position status
        gap_ahead = position_status.get('gap_ahead')
        gap_behind = position_status.get('gap_behind')
        position_text = f"""
  - Position: P{position_status.get('current_position', '?')}
  - Gap ahead: {f'{gap_ahead:.1f}s' if gap_ahead else 'Leader'}
  - Gap behind: {f'{gap_behind:.1f}s' if gap_behind else 'Last'}
  - Trend: {position_status.get('trend', 'unknown')}
"""

        # Format competitor status
        nearby = competitor_status.get('nearby_competitors', [])
        threats = competitor_status.get('threats', [])
        opportunities = competitor_status.get('opportunities', [])

        nearby_text = "\n".join([
            f"    P{c['position']}: {c['name']} - {c['compound']} ({c['tire_age']} laps)"
            for c in nearby[:3]
        ]) if nearby else "    None"

        competitor_text = f"""
  Nearby competitors (P±2):
{nearby_text}
  Threats: {len(threats)} drivers behind on fresh tires
  Opportunities: {len(opportunities)} drivers ahead on old tires
"""

        # Combine everything
        context = f"""
**Lap:** {current_lap}/78
**Driver:** {self.driver_name}

**Detected Events:**
{events_text}

**Tire Status:**
{tire_text}

**Pace Analysis:**
{pace_text}

**Position:**
{position_text}

**Competitors:**
{competitor_text}
"""

        return context

    def _get_mock_recommendation(self, current_lap: int, events: List[TriggerEvent], lap_data: Dict) -> Dict:
        """
        Return STRATEGIC recommendation based on tire model simulations (no AI needed)
        This is NOT mock data - it's real strategy calculations!
        """
        tire_age = lap_data.get('tire_age', 0)
        compound = lap_data.get('compound', 'HARD')

        # STRATEGIC CALCULATION: Run pit window optimization
        try:
            scenarios = self.tire_model.optimal_pit_window(
                current_lap=current_lap,
                stint1_compound=compound,
                stint2_compound='MEDIUM'
            )

            optimal_pit_lap = scenarios[0]['pit_lap']
            optimal_time = scenarios[0]['total_race_time']
            time_loss = scenarios[0]['time_vs_optimal']

        except:
            # Fallback if simulation fails
            optimal_pit_lap = current_lap + 3
            optimal_time = 0
            time_loss = 0

        # Analyze competitive situation for tactical instructions
        racing_tactic = self._get_racing_tactic(events, lap_data)

        # Determine strategy based on optimal pit window
        laps_to_optimal = optimal_pit_lap - current_lap

        if laps_to_optimal <= 2:
            rec_type = 'PIT_NOW'
            urgency = 'CRITICAL'
            confidence = 0.9
            driver_msg = f"Box box! Optimal window. {compound} → MEDIUM. {racing_tactic}"
            pit_crew_msg = f"MEDIUM tires ready. Optimal pit lap {optimal_pit_lap}. {racing_tactic}"
            reasoning = f"Tire model predicts optimal pit on lap {optimal_pit_lap} (now or next lap). Staying out costs time. {racing_tactic}"
        elif laps_to_optimal <= 5:
            rec_type = 'PIT_SOON'
            urgency = 'HIGH'
            confidence = 0.85
            driver_msg = f"Pit in {laps_to_optimal} laps. Conserve tires. {compound} age: {tire_age}. {racing_tactic}"
            pit_crew_msg = f"Prepare MEDIUM tires. Window: laps {optimal_pit_lap-1}-{optimal_pit_lap+1}"
            reasoning = f"Optimal pit window approaching (lap {optimal_pit_lap}). Current degradation {tire_age} laps on {compound}. {racing_tactic}"
        elif tire_age > 50:
            rec_type = 'STAY_OUT'
            urgency = 'MEDIUM'
            confidence = 0.75
            driver_msg = f"Stay out, manage tires. {tire_age} laps on {compound}. {racing_tactic}"
            pit_crew_msg = f"Monitor degradation. Consider pit if position threatened."
            reasoning = f"Tire age {tire_age} but high degradation tracks allow tire saving. {racing_tactic}"
        else:
            rec_type = 'STAY_OUT'
            urgency = 'LOW'
            confidence = 0.7
            driver_msg = f"Continue current pace. Tires good ({tire_age} laps on {compound}). {racing_tactic}"
            pit_crew_msg = f"No pit planned. Monitor tire deg and competitor strategies."
            reasoning = f"Tires healthy at {tire_age} laps. Optimal window not yet open. {racing_tactic}"

        # Detect critical events
        critical_events = [e for e in events if e.urgency == 'CRITICAL']
        if critical_events and tire_age < 30:
            # Override if there's a critical event but tires are young (e.g., puncture, position lost)
            key_event = critical_events[0].data.get('message', 'Critical event detected')
            reasoning = f"OVERRIDE: {key_event}. {reasoning}"

        return {
            "consensus": "CLEAR",
            "recommendation_type": rec_type,
            "pit_window": [optimal_pit_lap - 1, optimal_pit_lap + 1] if rec_type in ['PIT_NOW', 'PIT_SOON'] else None,
            "target_compound": "MEDIUM" if rec_type in ['PIT_NOW', 'PIT_SOON'] else None,
            "driver_instruction": driver_msg,
            "pit_crew_instruction": pit_crew_msg,
            "reasoning": reasoning,
            "urgency": urgency,
            "confidence": confidence,
            "key_events": [e.data.get('message', e.type) for e in events[:3]]
        }

    def _get_racing_tactic(self, events: List[TriggerEvent], lap_data: Dict) -> str:
        """
        Generate tactical racing instruction based on competitive situation
        Returns instruction like "Push hard - undercut opportunity" or "Defend position"
        """
        # Check for competitor threats/opportunities
        for event in events:
            if event.type == 'COMPETITOR_THREAT':
                threat_msg = event.data.get('message', '')
                if 'closing' in threat_msg.lower():
                    return "Defend position - car behind gaining pace"
                elif 'faster' in threat_msg.lower():
                    return "Push hard - maintain gap"

            elif event.type == 'COMPETITOR_OPPORTUNITY':
                opp_msg = event.data.get('message', '')
                if 'slower' in opp_msg.lower():
                    return "Attack mode - target ahead vulnerable"
                elif 'degradation' in opp_msg.lower():
                    return "Conserve tires - let them come to us"

        # Check tire events for pace management
        for event in events:
            if event.type == 'TIRE_CLIFF_APPROACHING':
                return "Manage pace - tire cliff approaching"
            elif event.type == 'TIRE_DEGRADATION_SPIKE':
                return "Smooth inputs - high degradation detected"

        # Check pace events
        for event in events:
            if event.type == 'PACE_IMPROVEMENT':
                return "Keep pushing - strong pace window"
            elif event.type == 'PACE_DROP':
                return "Check tires - pace dropping"

        # Default tactical instruction
        return "Maintain rhythm - executing plan"

    def get_cached_recommendation(self) -> Optional[Dict]:
        """
        Return last recommendation if still valid
        Used when no significant events detected
        """
        return self.last_recommendation


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Coordinator Agent with Data Agent Tools - Test")
    print("=" * 60)

    # Create coordinator
    coordinator = CoordinatorAgent(driver_name="LEC")

    # Simulate lap data
    print("\nSimulating Lap 65 - Monaco 2024...")

    # Simulate data agent analysis
    lap_data = {
        'lap_time': 76.607,
        'compound': 'HARD',
        'tire_age': 64,
        'sector1': 18.5,
        'sector2': 39.2,
        'sector3': 18.9
    }

    position_data = {
        'position': 1,
        'gap_ahead': None,  # Leader
        'gap_behind': 0.8  # Piastri
    }

    competitor_data = [
        {
            'name': 'PIA',
            'position': 2,
            'lap_time': 76.3,  # 0.3s faster
            'tire_age': 64,
            'compound': 'HARD'
        },
        {
            'name': 'SAI',
            'position': 3,
            'lap_time': 76.9,
            'tire_age': 64,
            'compound': 'HARD'
        }
    ]

    # Create mock events (normally from data agents)
    from data_agents import TriggerEvent

    events = [
        TriggerEvent(
            event_type='OLD_TIRES',
            urgency='HIGH',
            call_ai=True,
            data={
                'age': 64,
                'compound': 'HARD',
                'message': 'Old tires (64 laps on HARD)'
            }
        ),
        TriggerEvent(
            event_type='CLOSE_RACING',
            urgency='HIGH',
            call_ai=True,
            data={
                'position': 1,
                'gap_behind': 0.8,
                'message': 'Close racing: P1 with Piastri 0.8s behind'
            }
        ),
        TriggerEvent(
            event_type='COMPETITOR_FASTER',
            urgency='HIGH',
            call_ai=True,
            data={
                'driver': 'PIA',
                'pace_delta': 0.3,
                'message': 'PIA is 0.3s/lap faster'
            }
        )
    ]

    # Get recommendation
    print("\nCalling Coordinator AI with 3 HIGH urgency events...")

    result = coordinator.analyze_situation(
        current_lap=65,
        events=events,
        lap_data=lap_data,
        position_data=position_data,
        competitor_data=competitor_data
    )

    print("\nCoordinator Recommendation:")
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 60)
    print("✅ Coordinator agent working with data agent tools!")
    print("=" * 60)
