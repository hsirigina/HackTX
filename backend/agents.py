"""
AI Agents for F1 Race Strategy System.
Three specialized agents: Tire Strategist, Competitor Tracker, and Coordinator.
"""
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from tire_model import TireDegradationModel

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(self, name: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize base agent.

        Args:
            name: Agent name (e.g., "Tire Strategist")
            model_name: Gemini model to use
        """
        self.name = name
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.conversation_history = []

    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate response using Gemini.

        Args:
            prompt: User prompt
            context: Optional context to include

        Returns:
            Agent's response
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

    def analyze_with_json(self, prompt: str, context: str) -> Dict:
        """
        Generate structured JSON response.

        Args:
            prompt: Analysis prompt
            context: Data context

        Returns:
            Parsed JSON response
        """
        full_prompt = f"{context}\n\n{prompt}\n\nRespond ONLY with valid JSON, no other text."

        try:
            response = self.model.generate_content(full_prompt)
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response_text[:200]}")
            return {"error": "Failed to parse JSON response", "raw": response_text}
        except Exception as e:
            return {"error": str(e)}


class TireAgent(BaseAgent):
    """
    Tire Strategist Agent - Analyzes tire degradation and pit windows.
    """

    SYSTEM_PROMPT = """You are the Tire Strategist agent for an F1 team. Your sole responsibility is analyzing tire performance and degradation.

Your tasks:
1. Analyze tire degradation rate using the provided tire model
2. Predict when performance will fall off a "cliff"
3. Recommend optimal pit window (lap range)
4. Assess urgency (LOW/MEDIUM/HIGH/CRITICAL)

Be concise. Speak in race engineer language. Focus only on tire performance."""

    def __init__(self):
        super().__init__("Tire Strategist")
        self.tire_model = TireDegradationModel(total_laps=78)

    def analyze(
        self,
        current_lap: int,
        tire_compound: str,
        tire_age: int,
        recent_lap_times: List[float],
        track_temp: float = 30.0
    ) -> Dict:
        """
        Analyze tire strategy.

        Args:
            current_lap: Current lap number
            tire_compound: Current tire compound
            tire_age: Laps on current tires
            recent_lap_times: Last 5 lap times
            track_temp: Track temperature in Celsius

        Returns:
            {
                "status": "OK" | "WARNING" | "CRITICAL",
                "recommendation": "PIT_NOW" | "PIT_SOON" | "TIRES_OK",
                "pit_window": [15, 18],
                "reasoning": "...",
                "urgency": "HIGH",
                "confidence": 0.85
            }
        """
        # Use tire model to calculate degradation
        degradation = self.tire_model.get_degradation_rate(tire_compound, tire_age)
        cliff_lap = self.tire_model.predict_tire_cliff(tire_compound, threshold=2.0)

        # Calculate optimal pit window
        scenarios = self.tire_model.optimal_pit_window(
            current_lap=current_lap,
            stint1_compound=tire_compound,
            stint2_compound='MEDIUM'  # Assume MEDIUM for second stint
        )

        optimal_pit_lap = scenarios[0]['pit_lap']
        pit_window_start = max(current_lap, optimal_pit_lap - 2)
        pit_window_end = optimal_pit_lap + 2

        # Build context for Gemini
        context = f"""
Current Race State:
- Lap: {current_lap}/78
- Tire: {tire_compound} (age: {tire_age} laps)
- Degradation: +{degradation:.3f}s vs fresh tire
- Performance cliff predicted at lap {cliff_lap}
- Recent lap times: {recent_lap_times}

Tire Model Analysis:
- Optimal pit lap: {optimal_pit_lap}
- Recommended window: laps {pit_window_start}-{pit_window_end}
- Time difference vs optimal: {scenarios[0]['time_vs_optimal']:.1f}s
"""

        prompt = f"""{self.SYSTEM_PROMPT}

Analyze the tire situation and provide a recommendation in JSON format:

{{
    "status": "OK" | "WARNING" | "CRITICAL",
    "recommendation": "PIT_NOW" | "PIT_SOON" | "TIRES_OK",
    "pit_window": [start_lap, end_lap],
    "reasoning": "Brief explanation (1-2 sentences)",
    "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "confidence": 0.0-1.0
}}

Consider:
- Is the tire close to the cliff?
- Are we in the optimal pit window?
- Is degradation accelerating?"""

        return self.analyze_with_json(prompt, context)


class CompetitorAgent(BaseAgent):
    """
    Competitor Tracker Agent - Monitors opponents and identifies strategic opportunities.
    """

    SYSTEM_PROMPT = """You are the Competitor Tracker agent for an F1 team. You monitor opponents and identify strategic opportunities.

Your tasks:
1. Detect opponent pace changes (improving/fading)
2. Identify undercut/overcut opportunities
3. Predict competitor pit strategies
4. Assess position gain/loss for different strategies

Be tactical. Think like a race strategist. Focus on competitive advantage."""

    def __init__(self):
        super().__init__("Competitor Tracker")

    def analyze(
        self,
        current_lap: int,
        our_position: int,
        our_lap_time: float,
        competitors: List[Dict]
    ) -> Dict:
        """
        Analyze competitor strategies.

        Args:
            current_lap: Current lap number
            our_position: Our current position
            our_lap_time: Our last lap time
            competitors: List of competitor data:
                [{
                    "position": 2,
                    "driver": "VER",
                    "lap_time": 77.5,
                    "gap": +2.3,
                    "tire_age": 15,
                    "compound": "MEDIUM"
                }, ...]

        Returns:
            {
                "status": "OK" | "OPPORTUNITY" | "THREAT",
                "recommendation": "COUNTER_STRATEGY" | "UNDERCUT" | "OVERCUT" | "STAY_OUT",
                "target_driver": "VER",
                "reasoning": "...",
                "position_impact": "...",
                "confidence": 0.78
            }
        """
        # Build context
        competitor_info = "\n".join([
            f"  P{c['position']}: {c['driver']} - {c['lap_time']:.2f}s (tire: {c['compound']}, age: {c['tire_age']})"
            for c in competitors[:5]  # Top 5 competitors
        ])

        context = f"""
Current Race State:
- Lap: {current_lap}/78
- Our Position: P{our_position}
- Our Lap Time: {our_lap_time:.2f}s

Competitors:
{competitor_info}
"""

        prompt = f"""{self.SYSTEM_PROMPT}

Analyze competitor strategies and provide recommendation in JSON format:

{{
    "status": "OK" | "OPPORTUNITY" | "THREAT",
    "recommendation": "COUNTER_STRATEGY" | "UNDERCUT" | "OVERCUT" | "STAY_OUT",
    "target_driver": "3-letter driver code or null",
    "reasoning": "Brief explanation (1-2 sentences)",
    "position_impact": "Expected position change if we follow recommendation",
    "confidence": 0.0-1.0
}}

Consider:
- Are any competitors losing pace (opportunity)?
- Are faster cars behind us (threat)?
- Can we undercut/overcut someone ahead?"""

        return self.analyze_with_json(prompt, context)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent - Synthesizes inputs from specialist agents and makes final recommendations.
    """

    SYSTEM_PROMPT = """You are the Coordinator agent. You synthesize inputs from the Tire Agent and Competitor Agent to make final strategy recommendations.

Your tasks:
1. Identify if agents agree or disagree
2. Resolve conflicts by weighing confidence scores and race context
3. Present top 2-3 strategies with trade-offs
4. Provide clear, actionable recommendations

Speak in plain English. Make the complex simple. Help humans decide under pressure."""

    def __init__(self):
        super().__init__("Coordinator")

    def synthesize(
        self,
        current_lap: int,
        tire_agent_output: Dict,
        competitor_agent_output: Dict,
        race_context: Dict
    ) -> Dict:
        """
        Synthesize agent recommendations into final strategy.

        Args:
            current_lap: Current lap number
            tire_agent_output: Tire agent's recommendation
            competitor_agent_output: Competitor agent's recommendation
            race_context: Additional race context (position, gap, etc.)

        Returns:
            {
                "consensus": "UNANIMOUS" | "SPLIT" | "CONFLICT",
                "top_strategies": [
                    {
                        "id": "A",
                        "name": "PIT LAP 15 (AGGRESSIVE)",
                        "win_probability": 0.68,
                        "trade_off": "...",
                        "supporting_agents": ["TIRE", "COMPETITOR"]
                    }, ...
                ],
                "recommended_strategy": "A",
                "reasoning": "..."
            }
        """
        # Build context
        context = f"""
Current Lap: {current_lap}/78
Position: P{race_context.get('position', '?')}

TIRE AGENT says:
- Status: {tire_agent_output.get('status')}
- Recommendation: {tire_agent_output.get('recommendation')}
- Pit Window: {tire_agent_output.get('pit_window')}
- Reasoning: {tire_agent_output.get('reasoning')}
- Urgency: {tire_agent_output.get('urgency')}
- Confidence: {tire_agent_output.get('confidence')}

COMPETITOR AGENT says:
- Status: {competitor_agent_output.get('status')}
- Recommendation: {competitor_agent_output.get('recommendation')}
- Target: {competitor_agent_output.get('target_driver')}
- Reasoning: {competitor_agent_output.get('reasoning')}
- Position Impact: {competitor_agent_output.get('position_impact')}
- Confidence: {competitor_agent_output.get('confidence')}
"""

        prompt = f"""{self.SYSTEM_PROMPT}

Synthesize the agent recommendations and provide final strategy in JSON format:

{{
    "consensus": "UNANIMOUS" | "SPLIT" | "CONFLICT",
    "top_strategies": [
        {{
            "id": "A",
            "name": "Brief strategy name",
            "win_probability": 0.0-1.0,
            "trade_off": "What we gain vs what we lose",
            "supporting_agents": ["TIRE", "COMPETITOR"] or ["TIRE"] or ["COMPETITOR"]
        }},
        // Include 2-3 strategies
    ],
    "recommended_strategy": "A",
    "reasoning": "Why this is the best option (2-3 sentences)"
}}

Consensus rules:
- UNANIMOUS: Both agents agree
- SPLIT: Agents disagree but both valid
- CONFLICT: Strong disagreement, unclear path

Provide strategies even if agents disagree - show trade-offs for each option."""

        return self.analyze_with_json(prompt, context)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("AI Agents Test")
    print("=" * 60)

    # Test Tire Agent
    print("\n1. Testing Tire Agent...")
    tire_agent = TireAgent()

    tire_result = tire_agent.analyze(
        current_lap=30,
        tire_compound='SOFT',
        tire_age=15,
        recent_lap_times=[77.2, 77.5, 77.8, 78.1, 78.4],
        track_temp=32.0
    )

    print(f"Tire Agent Result:")
    print(json.dumps(tire_result, indent=2))

    # Test Competitor Agent
    print("\n2. Testing Competitor Agent...")
    comp_agent = CompetitorAgent()

    comp_result = comp_agent.analyze(
        current_lap=30,
        our_position=2,
        our_lap_time=77.5,
        competitors=[
            {"position": 1, "driver": "LEC", "lap_time": 77.2, "gap": -2.3, "tire_age": 29, "compound": "HARD"},
            {"position": 3, "driver": "VER", "lap_time": 78.5, "gap": +5.1, "tire_age": 28, "compound": "HARD"},
        ]
    )

    print(f"Competitor Agent Result:")
    print(json.dumps(comp_result, indent=2))

    # Test Coordinator
    print("\n3. Testing Coordinator Agent...")
    coord_agent = CoordinatorAgent()

    coord_result = coord_agent.synthesize(
        current_lap=30,
        tire_agent_output=tire_result,
        competitor_agent_output=comp_result,
        race_context={"position": 2, "gap_ahead": -2.3, "gap_behind": +5.1}
    )

    print(f"Coordinator Result:")
    print(json.dumps(coord_result, indent=2))

    print("\n" + "=" * 60)
    print("✅ All agents working!")
    print("=" * 60)
