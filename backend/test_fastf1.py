"""
Test script to explore FastF1 and find exciting races for demo.
"""
import fastf1
import os

# Enable cache to speed up data loading
cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

def explore_2024_races():
    """List all 2024 races to pick an exciting one for demo."""
    print("🏎️  F1 2024 Race Calendar\n")

    schedule = fastf1.get_event_schedule(2024)

    # Filter only race events (not testing, sprint qualifying, etc.)
    races = schedule[schedule['EventFormat'] != 'testing']

    print(f"Total races in 2024: {len(races)}\n")
    print("Notable races for demo:\n")

    # Highlight some exciting races
    exciting_races = ['Monaco', 'Singapore', 'Abu Dhabi', 'Suzuka', 'Spa']

    for idx, row in races.iterrows():
        event_name = row['EventName']
        round_num = row['RoundNumber']
        location = row['Location']

        if any(name in event_name for name in exciting_races):
            print(f"  ⭐ Round {round_num}: {event_name} ({location})")
        else:
            print(f"     Round {round_num}: {event_name} ({location})")

    return races

def load_race_preview(year, race_name):
    """Load a specific race and show basic info."""
    print(f"\n📊 Loading {year} {race_name}...\n")

    try:
        # Load race session
        session = fastf1.get_session(year, race_name, 'R')  # 'R' = Race
        session.load()

        print(f"Race: {session.event['EventName']}")
        print(f"Date: {session.event['EventDate']}")
        print(f"Location: {session.event['Location']}")
        print(f"Total Laps: {session.total_laps}")

        # Get lap data for first 5 drivers
        print(f"\nDrivers and Lap Count:")
        results = session.results
        for idx, driver in results.head(10).iterrows():
            driver_num = driver['DriverNumber']
            abbr = driver['Abbreviation']
            full_name = driver['FullName']
            team = driver['TeamName']
            position = driver['Position']

            print(f"  P{position}: {abbr} ({driver_num}) - {full_name} - {team}")

        # Check for interesting strategic moments (pit stops)
        print(f"\nPit Stop Summary:")
        laps = session.laps
        pit_stops = laps[laps['PitOutTime'].notna()]
        print(f"Total pit stops: {len(pit_stops)}")

        # Show pit stop distribution by lap
        if len(pit_stops) > 0:
            print(f"\nPit stops by lap range:")
            for lap_range in [(1, 15), (16, 30), (31, 45), (46, 100)]:
                start, end = lap_range
                stops_in_range = pit_stops[
                    (pit_stops['LapNumber'] >= start) &
                    (pit_stops['LapNumber'] <= end)
                ]
                if len(stops_in_range) > 0:
                    print(f"  Laps {start}-{end}: {len(stops_in_range)} stops")

        return session

    except Exception as e:
        print(f"Error loading race: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("FastF1 Test & Race Explorer")
    print("=" * 60)

    # List all 2024 races
    races = explore_2024_races()

    # Load a specific race for detailed analysis
    # Monaco is always strategic and exciting!
    print("\n" + "=" * 60)
    session = load_race_preview(2024, 'Monaco')

    if session:
        print("\n✅ FastF1 is working! Data loaded successfully.")
        print("\nRecommended races for demo:")
        print("  1. Monaco 2024 - Strategic, overtaking difficult, pit timing crucial")
        print("  2. Singapore 2024 - Night race, tire management critical")
        print("  3. Abu Dhabi 2024 - Season finale, potentially dramatic")
    else:
        print("\n⚠️  Could not load race data. Check internet connection.")
