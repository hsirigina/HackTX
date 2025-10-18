"""
Race Replay System - Streams historical F1 race data to Supabase in real-time.
Simulates a live race by pushing lap-by-lap data at configurable speed.
"""
import fastf1
import time
import os
import math
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

# Load environment variables
load_dotenv()

def safe_float(value) -> Optional[float]:
    """Convert value to float, handling NaN and None."""
    if value is None:
        return None
    try:
        float_val = float(value)
        if math.isnan(float_val) or math.isinf(float_val):
            return None
        return float_val
    except (ValueError, TypeError):
        return None

class RaceReplay:
    """
    Replays historical F1 races lap-by-lap to Supabase.
    """

    def __init__(
        self,
        race_id: str,
        supabase_url: str,
        supabase_key: str,
        laps_per_second: float = 0.5
    ):
        """
        Initialize race replay system.

        Args:
            race_id: Unique identifier for this race (e.g., "monaco_2024")
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            laps_per_second: Replay speed (0.5 = 1 lap every 2 seconds)
        """
        self.race_id = race_id
        self.laps_per_second = laps_per_second
        self.lap_interval = 1.0 / laps_per_second

        # Initialize Supabase client
        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Race data (loaded later)
        self.session = None
        self.laps_data = None
        self.results = None

    def load_race(self, year: int, race_name: str, session_type: str = 'R'):
        """
        Load historical race data from FastF1.

        Args:
            year: Race year (e.g., 2024)
            race_name: Race name (e.g., "Monaco")
            session_type: 'R' for Race, 'Q' for Qualifying, 'FP1', etc.
        """
        print(f"\n🏎️  Loading {year} {race_name} {session_type}...")

        # Enable FastF1 cache
        cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

        # Load session
        self.session = fastf1.get_session(year, race_name, session_type)
        self.session.load()

        # Get laps and results
        self.laps_data = self.session.laps
        self.results = self.session.results

        print(f"✅ Loaded {len(self.laps_data)} laps from {self.session.event['EventName']}")
        print(f"   Total race laps: {self.session.total_laps}")
        print(f"   Drivers: {len(self.results)}")

    def clear_race_data(self):
        """Clear existing race data from Supabase for fresh replay."""
        print(f"\n🗑️  Clearing existing data for race_id: {self.race_id}...")

        tables = ['lap_times', 'tire_data', 'pit_stops', 'race_positions', 'agent_recommendations']

        for table in tables:
            try:
                self.supabase.table(table).delete().eq('race_id', self.race_id).execute()
                print(f"   ✓ Cleared {table}")
            except Exception as e:
                print(f"   ⚠️  Error clearing {table}: {e}")

    def push_lap_data(self, lap_number: int):
        """
        Push data for a specific lap to Supabase.

        Args:
            lap_number: Lap number to push (1-indexed)
        """
        # Get all laps for this lap number
        lap_data = self.laps_data[self.laps_data['LapNumber'] == lap_number]

        if len(lap_data) == 0:
            return

        # Process each driver's lap
        for idx, lap in lap_data.iterrows():
            try:
                driver_num = int(lap['DriverNumber'])
                driver = lap['Driver']

                # Lap times (handle NaN values)
                lap_time = safe_float(lap['LapTime'].total_seconds() if not lap['LapTime'] is None else None)
                sector1 = safe_float(lap['Sector1Time'].total_seconds() if not lap['Sector1Time'] is None else None)
                sector2 = safe_float(lap['Sector2Time'].total_seconds() if not lap['Sector2Time'] is None else None)
                sector3 = safe_float(lap['Sector3Time'].total_seconds() if not lap['Sector3Time'] is None else None)

                # Insert lap time
                self.supabase.table('lap_times').insert({
                    'race_id': self.race_id,
                    'driver_number': driver_num,
                    'driver_name': driver,
                    'lap_number': int(lap_number),
                    'lap_time_seconds': lap_time,
                    'sector_1_time': sector1,
                    'sector_2_time': sector2,
                    'sector_3_time': sector3
                }).execute()

                # Tire data
                compound = lap['Compound']
                tire_life = lap['TyreLife']
                tire_age = int(tire_life) if not (tire_life is None or (isinstance(tire_life, float) and math.isnan(tire_life))) else 0

                if compound and compound != 'UNKNOWN' and not (isinstance(compound, float) and math.isnan(compound)):
                    self.supabase.table('tire_data').insert({
                        'race_id': self.race_id,
                        'driver_number': driver_num,
                        'lap_number': int(lap_number),
                        'compound': str(compound),
                        'tire_age': tire_age
                    }).execute()

                # Pit stops (if driver pitted this lap)
                pit_out_time = lap['PitOutTime']
                if not (pit_out_time is None or (isinstance(pit_out_time, float) and math.isnan(pit_out_time))):
                    pit_in_time = lap['PitInTime']
                    pit_duration = safe_float(pit_in_time.total_seconds() if not pit_in_time is None else None) or 25.0

                    self.supabase.table('pit_stops').insert({
                        'race_id': self.race_id,
                        'driver_number': driver_num,
                        'lap_number': int(lap_number),
                        'pit_duration_seconds': pit_duration
                    }).execute()

                # Race position
                pos = lap['Position']
                position = int(pos) if not (pos is None or (isinstance(pos, float) and math.isnan(pos))) else 99

                self.supabase.table('race_positions').insert({
                    'race_id': self.race_id,
                    'lap_number': int(lap_number),
                    'driver_number': driver_num,
                    'position': position,
                    'gap_to_leader_seconds': None  # Calculate if needed
                }).execute()

            except Exception as e:
                print(f"   ⚠️  Error pushing lap {lap_number} for driver {driver}: {e}")

    def replay(
        self,
        start_lap: int = 1,
        end_lap: Optional[int] = None,
        focused_driver: Optional[str] = None
    ):
        """
        Replay the race lap-by-lap.

        Args:
            start_lap: Starting lap number
            end_lap: Ending lap number (None = full race)
            focused_driver: Driver abbreviation to focus on (e.g., "LEC")
        """
        if self.session is None:
            raise ValueError("No race loaded. Call load_race() first.")

        if end_lap is None:
            end_lap = self.session.total_laps

        print(f"\n▶️  Starting replay: Laps {start_lap} to {end_lap}")
        print(f"   Replay speed: {self.laps_per_second} laps/second ({self.lap_interval:.1f}s per lap)")

        if focused_driver:
            print(f"   Focusing on driver: {focused_driver}")

        for lap_num in range(start_lap, end_lap + 1):
            lap_start_time = time.time()

            print(f"\n📊 Lap {lap_num}/{end_lap}")

            # Push data for this lap
            self.push_lap_data(lap_num)

            # Show focused driver info if specified
            if focused_driver:
                driver_lap = self.laps_data[
                    (self.laps_data['LapNumber'] == lap_num) &
                    (self.laps_data['Driver'] == focused_driver)
                ]

                if len(driver_lap) > 0:
                    lap_info = driver_lap.iloc[0]
                    position = lap_info['Position']
                    lap_time = lap_info['LapTime']
                    compound = lap_info['Compound']
                    tire_age = lap_info['TyreLife']

                    print(f"   {focused_driver}: P{position} | {lap_time} | {compound} (age: {tire_age})")

            # Sleep to maintain replay speed
            elapsed = time.time() - lap_start_time
            sleep_time = max(0, self.lap_interval - elapsed)
            time.sleep(sleep_time)

        print(f"\n✅ Replay complete! Pushed {end_lap - start_lap + 1} laps to Supabase.")


def main():
    """Main entry point for race replay."""

    # Load configuration from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return

    print("=" * 60)
    print("F1 Race Replay System")
    print("=" * 60)

    # Initialize replay
    replay = RaceReplay(
        race_id="monaco_2024",
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        laps_per_second=0.5  # 1 lap every 2 seconds
    )

    # Load Monaco 2024 race
    replay.load_race(2024, 'Monaco', 'R')

    # Clear existing data
    replay.clear_race_data()

    # Replay interesting portion of race (laps 60-78 = final stint)
    # For full demo, use start_lap=1, end_lap=78
    print("\n🎬 Starting replay of Monaco 2024 final stint (laps 60-78)...")
    print("   This is where Leclerc held off Piastri for the win!")

    replay.replay(
        start_lap=60,
        end_lap=78,
        focused_driver='LEC'  # Focus on race winner Charles Leclerc
    )

    print("\n" + "=" * 60)
    print("✅ Race replay finished!")
    print("   Data is now in Supabase and ready for AI agents to analyze.")
    print("=" * 60)


if __name__ == "__main__":
    main()
