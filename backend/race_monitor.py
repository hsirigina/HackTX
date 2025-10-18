"""
Race Monitor - Orchestrates AI agents to analyze live race data and generate recommendations.
Monitors Supabase for new lap data and triggers agent analysis.
"""
import os
import time
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from agents import TireAgent, CompetitorAgent, CoordinatorAgent

load_dotenv()


class RaceMonitor:
    """
    Monitors race data and orchestrates AI agents to generate recommendations.
    """

    def __init__(
        self,
        race_id: str,
        focused_driver: str,
        supabase_url: str,
        supabase_key: str
    ):
        """
        Initialize race monitor.

        Args:
            race_id: Race identifier (e.g., "monaco_2024")
            focused_driver: Driver to focus on (e.g., "LEC")
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.race_id = race_id
        self.focused_driver = focused_driver
        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Initialize agents
        print("🤖 Initializing AI agents...")
        self.tire_agent = TireAgent()
        self.competitor_agent = CompetitorAgent()
        self.coordinator_agent = CoordinatorAgent()
        print("   ✓ All agents ready")

        # Track last processed lap
        self.last_processed_lap = 0

    def get_latest_lap(self) -> Optional[int]:
        """Get the latest lap number in the database."""
        try:
            result = self.supabase.table('lap_times') \
                .select('lap_number') \
                .eq('race_id', self.race_id) \
                .order('lap_number', desc=True) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                return result.data[0]['lap_number']
            return None
        except Exception as e:
            print(f"Error getting latest lap: {e}")
            return None

    def get_driver_data(self, lap_number: int, driver: str) -> Optional[Dict]:
        """
        Get driver data for a specific lap.

        Args:
            lap_number: Lap number
            driver: Driver abbreviation

        Returns:
            Driver data or None
        """
        try:
            # Get lap time
            lap_result = self.supabase.table('lap_times') \
                .select('*') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .eq('driver_name', driver) \
                .execute()

            if not lap_result.data or len(lap_result.data) == 0:
                return None

            lap_data = lap_result.data[0]

            # Get tire data
            tire_result = self.supabase.table('tire_data') \
                .select('*') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .eq('driver_number', lap_data['driver_number']) \
                .execute()

            tire_data = tire_result.data[0] if tire_result.data else {}

            # Get position
            pos_result = self.supabase.table('race_positions') \
                .select('*') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .eq('driver_number', lap_data['driver_number']) \
                .execute()

            pos_data = pos_result.data[0] if pos_result.data else {}

            return {
                'lap_number': lap_number,
                'driver': driver,
                'driver_number': lap_data['driver_number'],
                'lap_time': lap_data.get('lap_time_seconds'),
                'position': pos_data.get('position'),
                'compound': tire_data.get('compound', 'UNKNOWN'),
                'tire_age': tire_data.get('tire_age', 0)
            }

        except Exception as e:
            print(f"Error getting driver data: {e}")
            return None

    def get_recent_lap_times(self, driver: str, current_lap: int, count: int = 5) -> List[float]:
        """Get recent lap times for a driver."""
        try:
            start_lap = max(1, current_lap - count + 1)

            result = self.supabase.table('lap_times') \
                .select('lap_time_seconds') \
                .eq('race_id', self.race_id) \
                .eq('driver_name', driver) \
                .gte('lap_number', start_lap) \
                .lte('lap_number', current_lap) \
                .order('lap_number', desc=False) \
                .execute()

            lap_times = [
                row['lap_time_seconds']
                for row in result.data
                if row['lap_time_seconds'] is not None
            ]

            return lap_times[-count:] if lap_times else []

        except Exception as e:
            print(f"Error getting recent lap times: {e}")
            return []

    def get_competitors(self, lap_number: int, our_position: int) -> List[Dict]:
        """Get competitor data for a lap."""
        try:
            # Get all positions for this lap
            result = self.supabase.table('race_positions') \
                .select('driver_number, position') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .order('position', desc=False) \
                .execute()

            competitors = []

            for pos_data in result.data:
                # Get lap time
                lap_result = self.supabase.table('lap_times') \
                    .select('driver_name, lap_time_seconds') \
                    .eq('race_id', self.race_id) \
                    .eq('lap_number', lap_number) \
                    .eq('driver_number', pos_data['driver_number']) \
                    .execute()

                if not lap_result.data:
                    continue

                # Get tire data
                tire_result = self.supabase.table('tire_data') \
                    .select('compound, tire_age') \
                    .eq('race_id', self.race_id) \
                    .eq('lap_number', lap_number) \
                    .eq('driver_number', pos_data['driver_number']) \
                    .execute()

                tire_data = tire_result.data[0] if tire_result.data else {}
                lap_data = lap_result.data[0]

                competitors.append({
                    'position': pos_data['position'],
                    'driver': lap_data['driver_name'],
                    'lap_time': lap_data['lap_time_seconds'] or 77.0,
                    'gap': 0.0,  # Calculate if needed
                    'tire_age': tire_data.get('tire_age', 0),
                    'compound': tire_data.get('compound', 'UNKNOWN')
                })

            return competitors

        except Exception as e:
            print(f"Error getting competitors: {e}")
            return []

    def save_recommendation(self, lap_number: int, agent_name: str, recommendation: Dict):
        """Save agent recommendation to database."""
        try:
            self.supabase.table('agent_recommendations').insert({
                'race_id': self.race_id,
                'lap_number': lap_number,
                'agent_name': agent_name,
                'recommendation_type': recommendation.get('recommendation', 'UNKNOWN'),
                'confidence_score': recommendation.get('confidence', 0.0),
                'reasoning': recommendation.get('reasoning', '')
            }).execute()
        except Exception as e:
            print(f"Error saving recommendation: {e}")

    def analyze_lap(self, lap_number: int):
        """
        Analyze a specific lap with all agents.

        Args:
            lap_number: Lap number to analyze
        """
        print(f"\n{'='*60}")
        print(f"📊 Analyzing Lap {lap_number}")
        print(f"{'='*60}")

        # Get our driver's data
        our_data = self.get_driver_data(lap_number, self.focused_driver)

        if not our_data:
            print(f"⚠️  No data for {self.focused_driver} on lap {lap_number}")
            return

        print(f"\n{self.focused_driver} Status:")
        print(f"  Position: P{our_data['position']}")
        print(f"  Lap Time: {our_data['lap_time']:.2f}s" if our_data['lap_time'] else "  Lap Time: N/A")
        print(f"  Tire: {our_data['compound']} (age: {our_data['tire_age']} laps)")

        # Get recent lap times
        recent_laps = self.get_recent_lap_times(self.focused_driver, lap_number, count=5)

        # Only analyze every 5 laps to reduce API calls (or if tire is old)
        should_analyze = (lap_number % 5 == 0) or (our_data['tire_age'] > 20)

        if not should_analyze and lap_number > 5:
            print(f"\n⏭️  Skipping detailed analysis (analyzing every 5 laps)")
            return

        print(f"\n🔍 Running agent analysis...")

        # 1. Tire Agent Analysis
        print(f"\n1️⃣  Tire Agent analyzing...")
        tire_recommendation = self.tire_agent.analyze(
            current_lap=lap_number,
            tire_compound=our_data['compound'],
            tire_age=our_data['tire_age'],
            recent_lap_times=recent_laps,
            track_temp=30.0
        )

        print(f"   Status: {tire_recommendation.get('status', 'UNKNOWN')}")
        print(f"   Recommendation: {tire_recommendation.get('recommendation', 'UNKNOWN')}")
        print(f"   Reasoning: {tire_recommendation.get('reasoning', 'N/A')}")
        print(f"   Confidence: {tire_recommendation.get('confidence', 0.0):.0%}")

        self.save_recommendation(lap_number, 'TIRE', tire_recommendation)

        # 2. Competitor Agent Analysis
        print(f"\n2️⃣  Competitor Agent analyzing...")
        competitors = self.get_competitors(lap_number, our_data['position'])

        competitor_recommendation = self.competitor_agent.analyze(
            current_lap=lap_number,
            our_position=our_data['position'],
            our_lap_time=our_data['lap_time'] or 77.0,
            competitors=competitors
        )

        print(f"   Status: {competitor_recommendation.get('status', 'UNKNOWN')}")
        print(f"   Recommendation: {competitor_recommendation.get('recommendation', 'UNKNOWN')}")
        print(f"   Reasoning: {competitor_recommendation.get('reasoning', 'N/A')}")
        print(f"   Confidence: {competitor_recommendation.get('confidence', 0.0):.0%}")

        self.save_recommendation(lap_number, 'COMPETITOR', competitor_recommendation)

        # 3. Coordinator Agent Synthesis
        print(f"\n3️⃣  Coordinator synthesizing...")
        coordinator_output = self.coordinator_agent.synthesize(
            current_lap=lap_number,
            tire_agent_output=tire_recommendation,
            competitor_agent_output=competitor_recommendation,
            race_context={
                'position': our_data['position'],
                'compound': our_data['compound'],
                'tire_age': our_data['tire_age']
            }
        )

        print(f"   Consensus: {coordinator_output.get('consensus', 'UNKNOWN')}")
        print(f"   Recommended Strategy: {coordinator_output.get('recommended_strategy', 'N/A')}")
        print(f"   Reasoning: {coordinator_output.get('reasoning', 'N/A')}")

        # Show top strategies
        strategies = coordinator_output.get('top_strategies', [])
        if strategies:
            print(f"\n   Top Strategies:")
            for i, strategy in enumerate(strategies[:3], 1):
                print(f"     {i}. {strategy.get('name', 'Unknown')}")
                print(f"        Win Probability: {strategy.get('win_probability', 0.0):.0%}")
                print(f"        Trade-off: {strategy.get('trade_off', 'N/A')}")

        self.save_recommendation(lap_number, 'COORDINATOR', coordinator_output)

    def monitor(self, poll_interval: float = 2.0):
        """
        Monitor race and analyze new laps as they come in.

        Args:
            poll_interval: How often to check for new laps (seconds)
        """
        print(f"\n{'='*60}")
        print(f"🏁 Race Monitor Starting")
        print(f"{'='*60}")
        print(f"Race ID: {self.race_id}")
        print(f"Focused Driver: {self.focused_driver}")
        print(f"Poll Interval: {poll_interval}s")
        print(f"\nWaiting for race data...\n")

        try:
            while True:
                # Get latest lap in database
                latest_lap = self.get_latest_lap()

                if latest_lap is None:
                    print("⏳ No race data yet...")
                    time.sleep(poll_interval)
                    continue

                # If we have new laps, analyze them
                if latest_lap > self.last_processed_lap:
                    for lap in range(self.last_processed_lap + 1, latest_lap + 1):
                        self.analyze_lap(lap)
                        self.last_processed_lap = lap

                # Wait before checking again
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print("🛑 Race Monitor Stopped")
            print(f"{'='*60}")
            print(f"Last processed lap: {self.last_processed_lap}")


def main():
    """Main entry point."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key or google_api_key == 'your_google_gemini_api_key_here':
        print("❌ Error: GOOGLE_API_KEY must be set in .env")
        print("Get free key at: https://aistudio.google.com/app/apikey")
        return

    # Initialize monitor
    monitor = RaceMonitor(
        race_id="monaco_2024",
        focused_driver="LEC",  # Charles Leclerc (race winner)
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )

    # Start monitoring
    monitor.monitor(poll_interval=2.0)


if __name__ == "__main__":
    main()
