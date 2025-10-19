"""
Test complete data pipeline: FastF1 → Replay → Database → Monitor
"""
import fastf1
from race_replay import RaceReplay
from race_monitor_v2 import RaceMonitorV2
import os
from dotenv import load_dotenv

load_dotenv('/Users/harsh/Documents/GitHub/HackTX/.env')

cache_dir = os.path.expanduser('~/.fastf1_cache')
fastf1.Cache.enable_cache(cache_dir)

# Initialize replay
replay = RaceReplay(
    race_id='monaco_2024_test',
    supabase_url=os.getenv('SUPABASE_URL'),
    supabase_key=os.getenv('SUPABASE_KEY'),
    laps_per_second=10
)

# Load race
print('Loading Monaco 2024...')
replay.load_race(year=2024, race_name='Monaco')

# Clear old data
print('Clearing old data...')
replay.clear_race_data()

# Push 3 laps
print('\nPushing laps 60-62...')
for lap in range(60, 63):
    replay.push_lap_data(lap)
    print(f'  ✓ Lap {lap}')

# Initialize monitor
print('\nInitializing monitor...')
monitor = RaceMonitorV2(
    driver_name='LEC',
    race_id='monaco_2024_test',
    use_arduino=False
)

# Test data retrieval
print('\nTesting data retrieval...')
lap_data = monitor._get_latest_lap_data()

if lap_data:
    print(f'\n✅ SUCCESS - Retrieved lap {lap_data["lap_number"]}:')
    print(f'   Position: {lap_data.get("position")}')
    print(f'   Lap time: {lap_data.get("lap_time")}')
    print(f'   Tire: {lap_data.get("compound")} (age {lap_data.get("tire_age")})')
    print(f'   All drivers count: {len(lap_data.get("all_drivers", []))}')

    if lap_data.get('position') is None:
        print('\n❌ POSITION IS NONE - DATA PIPELINE BROKEN')
    else:
        print('\n✅ Position data valid - pipeline working correctly')
else:
    print('\n❌ FAILED - No lap data retrieved')

# Cleanup
print('\nCleaning up test data...')
replay.clear_race_data()
print('✅ Done')
