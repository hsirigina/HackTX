"""
Optimized Race Monitor - Smart event-based agent triggering.
Uses intelligent heuristics to minimize API calls while maximizing insights.
"""
import os
import time
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from agents import TireAgent, CompetitorAgent, CoordinatorAgent

load_dotenv()


class OptimizedRaceMonitor:
    """
    Smart race monitor that triggers agents based on race events, not lap intervals.
    """

    def __init__(
        self,
        race_id: str,
        focused_driver: str,
        supabase_url: str,
        supabase_key: str
    ):
        self.race_id = race_id
        self.focused_driver = focused_driver
        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Initialize agents
        print("🤖 Initializing AI agents...")
        self.tire_agent = TireAgent()
        self.competitor_agent = CompetitorAgent()
        self.coordinator_agent = CoordinatorAgent()
        print("   ✓ All agents ready")

        self.last_processed_lap = 0

        # Track state for smart triggering
        self.last_tire_analysis_lap = 0
        self.last_competitor_analysis_lap = 0
        self.last_full_analysis_lap = 0
        self.last_pit_stop_lap = 0
        self.last_tire_compound = None
        self.last_tire_age = 0

        # Cached recommendations
        self.cached_tire_recommendation = None
        self.cached_competitor_recommendation = None

        # API call counter
        self.api_calls_made = 0

    def should_analyze_tires(self, lap_number: int, tire_age: int, compound: str) -> bool:
        """
        Decide if we should run tire analysis.

        Triggers:
        - Every 10 laps minimum
        - Tire age > 20 laps (old tires)
        - Tire compound changed (pit stop)
        - Tire age jumps (pit stop detected)
        """
        # Always analyze first lap
        if self.last_tire_analysis_lap == 0:
            return True

        # Tire compound changed (pit stop!)
        if compound != self.last_tire_compound:
            print(f"   🔄 Tire change detected: {self.last_tire_compound} → {compound}")
            return True

        # Tire age reset (pit stop)
        if tire_age < self.last_tire_age - 5:
            print(f"   🔧 Pit stop detected (tire age reset)")
            return True

        # Old tires - analyze more frequently
        if tire_age > 20:
            laps_since = lap_number - self.last_tire_analysis_lap
            if laps_since >= 3:  # Every 3 laps for old tires
                print(f"   ⏰ Old tires ({tire_age} laps) - frequent check")
                return True

        # Regular interval
        laps_since = lap_number - self.last_tire_analysis_lap
        if laps_since >= 10:
            print(f"   ⏰ Periodic tire check (every 10 laps)")
            return True

        return False

    def should_analyze_competitors(self, lap_number: int, our_position: int) -> bool:
        """
        Decide if we should run competitor analysis.

        Triggers:
        - Every 15 laps minimum
        - Position changed
        - Close racing (top 3)
        - Pit stops detected nearby
        """
        # Always analyze first lap
        if self.last_competitor_analysis_lap == 0:
            return True

        # In top 3 - analyze more frequently
        if our_position <= 3:
            laps_since = lap_number - self.last_competitor_analysis_lap
            if laps_since >= 5:
                print(f"   🏆 Top 3 position - frequent competitor check")
                return True

        # Regular interval
        laps_since = lap_number - self.last_competitor_analysis_lap
        if laps_since >= 15:
            print(f"   ⏰ Periodic competitor check (every 15 laps)")
            return True

        return False

    def should_run_coordinator(self, lap_number: int) -> bool:
        """
        Decide if coordinator should synthesize.

        Only run if:
        - Both Tire and Competitor agents ran this lap
        - Or it's been 20 laps since last full analysis
        """
        # If both agents just ran, coordinator should synthesize
        if (self.last_tire_analysis_lap == lap_number and
            self.last_competitor_analysis_lap == lap_number):
            return True

        # Periodic full analysis
        laps_since = lap_number - self.last_full_analysis_lap
        if laps_since >= 20:
            print(f"   ⏰ Periodic full strategy review (every 20 laps)")
            return True

        return False

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
        """Get driver data for a specific lap."""
        try:
            lap_result = self.supabase.table('lap_times') \
                .select('*') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .eq('driver_name', driver) \
                .execute()

            if not lap_result.data or len(lap_result.data) == 0:
                return None

            lap_data = lap_result.data[0]

            tire_result = self.supabase.table('tire_data') \
                .select('*') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .eq('driver_number', lap_data['driver_number']) \
                .execute()

            tire_data = tire_result.data[0] if tire_result.data else {}

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
            result = self.supabase.table('race_positions') \
                .select('driver_number, position') \
                .eq('race_id', self.race_id) \
                .eq('lap_number', lap_number) \
                .order('position', desc=False) \
                .execute()

            competitors = []

            for pos_data in result.data:
                lap_result = self.supabase.table('lap_times') \
                    .select('driver_name, lap_time_seconds') \
                    .eq('race_id', self.race_id) \
                    .eq('lap_number', lap_number) \
                    .eq('driver_number', pos_data['driver_number']) \
                    .execute()

                if not lap_result.data:
                    continue

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
                    'gap': 0.0,
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
        Smart analysis - only calls agents when events warrant it.
        """
        print(f"\n{'='*60}")
        print(f"📊 Lap {lap_number} | API Calls: {self.api_calls_made}")
        print(f"{'='*60}")

        # Get our driver's data
        our_data = self.get_driver_data(lap_number, self.focused_driver)

        if not our_data:
            print(f"⚠️  No data for {self.focused_driver}")
            return

        print(f"\n{self.focused_driver} Status:")
        print(f"  Position: P{our_data['position']}")
        print(f"  Lap Time: {our_data['lap_time']:.2f}s" if our_data['lap_time'] else "  Lap Time: N/A")
        print(f"  Tire: {our_data['compound']} (age: {our_data['tire_age']} laps)")

        # Smart triggering decisions
        run_tire = self.should_analyze_tires(
            lap_number,
            our_data['tire_age'],
            our_data['compound']
        )

        run_competitor = self.should_analyze_competitors(
            lap_number,
            our_data['position']
        )

        # Update state
        self.last_tire_compound = our_data['compound']
        self.last_tire_age = our_data['tire_age']

        # Run Tire Agent if needed
        if run_tire:
            print(f"\n🔍 1️⃣  Tire Agent analyzing...")
            recent_laps = self.get_recent_lap_times(self.focused_driver, lap_number, count=5)

            self.cached_tire_recommendation = self.tire_agent.analyze(
                current_lap=lap_number,
                tire_compound=our_data['compound'],
                tire_age=our_data['tire_age'],
                recent_lap_times=recent_laps,
                track_temp=30.0
            )

            self.api_calls_made += 1
            self.last_tire_analysis_lap = lap_number

            print(f"   Status: {self.cached_tire_recommendation.get('status', 'UNKNOWN')}")
            print(f"   Rec: {self.cached_tire_recommendation.get('recommendation', 'UNKNOWN')}")
            print(f"   Reasoning: {self.cached_tire_recommendation.get('reasoning', 'N/A')}")

            self.save_recommendation(lap_number, 'TIRE', self.cached_tire_recommendation)
        else:
            print(f"\n⏭️  Tire Agent - Using cached recommendation")

        # Run Competitor Agent if needed
        if run_competitor:
            print(f"\n🔍 2️⃣  Competitor Agent analyzing...")
            competitors = self.get_competitors(lap_number, our_data['position'])

            self.cached_competitor_recommendation = self.competitor_agent.analyze(
                current_lap=lap_number,
                our_position=our_data['position'],
                our_lap_time=our_data['lap_time'] or 77.0,
                competitors=competitors
            )

            self.api_calls_made += 1
            self.last_competitor_analysis_lap = lap_number

            print(f"   Status: {self.cached_competitor_recommendation.get('status', 'UNKNOWN')}")
            print(f"   Rec: {self.cached_competitor_recommendation.get('recommendation', 'UNKNOWN')}")
            print(f"   Reasoning: {self.cached_competitor_recommendation.get('reasoning', 'N/A')}")

            self.save_recommendation(lap_number, 'COMPETITOR', self.cached_competitor_recommendation)
        else:
            print(f"\n⏭️  Competitor Agent - Using cached recommendation")

        # Run Coordinator if both agents have data
        if self.should_run_coordinator(lap_number):
            if self.cached_tire_recommendation and self.cached_competitor_recommendation:
                print(f"\n🔍 3️⃣  Coordinator synthesizing...")

                coordinator_output = self.coordinator_agent.synthesize(
                    current_lap=lap_number,
                    tire_agent_output=self.cached_tire_recommendation,
                    competitor_agent_output=self.cached_competitor_recommendation,
                    race_context={
                        'position': our_data['position'],
                        'compound': our_data['compound'],
                        'tire_age': our_data['tire_age']
                    }
                )

                self.api_calls_made += 1
                self.last_full_analysis_lap = lap_number

                print(f"   Consensus: {coordinator_output.get('consensus', 'UNKNOWN')}")
                print(f"   Strategy: {coordinator_output.get('recommended_strategy', 'N/A')}")
                print(f"   Reasoning: {coordinator_output.get('reasoning', 'N/A')}")

                strategies = coordinator_output.get('top_strategies', [])
                if strategies:
                    print(f"\n   Top Strategies:")
                    for i, strategy in enumerate(strategies[:2], 1):
                        print(f"     {i}. {strategy.get('name', 'Unknown')} - {strategy.get('win_probability', 0.0):.0%}")

                self.save_recommendation(lap_number, 'COORDINATOR', coordinator_output)
            else:
                print(f"\n⏭️  Coordinator - Waiting for agent data")

    def monitor(self, poll_interval: float = 1.0):
        """Monitor race with smart agent triggering."""
        print(f"\n{'='*60}")
        print(f"🏁 Optimized Race Monitor Starting")
        print(f"{'='*60}")
        print(f"Race ID: {self.race_id}")
        print(f"Focused Driver: {self.focused_driver}")
        print(f"Strategy: Smart event-based triggering")
        print(f"\nSmart Triggers:")
        print(f"  • Tire changes / pit stops")
        print(f"  • Old tires (>20 laps)")
        print(f"  • Top 3 racing")
        print(f"  • Periodic checks (tire:10 laps, competitor:15 laps)")
        print(f"\nThis minimizes API calls while staying responsive!\n")

        try:
            while True:
                latest_lap = self.get_latest_lap()

                if latest_lap is None:
                    print("⏳ No race data yet...")
                    time.sleep(poll_interval)
                    continue

                if latest_lap > self.last_processed_lap:
                    for lap in range(self.last_processed_lap + 1, latest_lap + 1):
                        self.analyze_lap(lap)
                        self.last_processed_lap = lap

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print("🛑 Race Monitor Stopped")
            print(f"{'='*60}")
            print(f"Laps processed: {self.last_processed_lap}")
            print(f"Total API calls: {self.api_calls_made}")
            print(f"Average: {self.api_calls_made / max(1, self.last_processed_lap):.2f} calls/lap")


def main():
    """Main entry point."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    if not google_api_key or google_api_key == 'your_google_gemini_api_key_here':
        print("❌ Error: GOOGLE_API_KEY must be set in .env")
        return

    monitor = OptimizedRaceMonitor(
        race_id="monaco_2024",
        focused_driver="LEC",
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )

    monitor.monitor(poll_interval=1.0)


if __name__ == "__main__":
    main()
