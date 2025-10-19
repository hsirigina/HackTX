"""
Debug script to test race replay and identify insertion failures
"""
import fastf1
from race_replay import RaceReplay
import os
from dotenv import load_dotenv

# Load env from file
load_dotenv('/Users/harsh/Documents/GitHub/HackTX/.env')

# Set up cache
cache_dir = os.path.expanduser('~/.fastf1_cache')
fastf1.Cache.enable_cache(cache_dir)

# Initialize replay
replay = RaceReplay(
    race_id='monaco_2024',
    supabase_url=os.getenv('SUPABASE_URL'),
    supabase_key=os.getenv('SUPABASE_KEY'),
    laps_per_second=10  # Fast replay
)

# Load race
print('Loading Monaco 2024 race data...')
replay.load_race(year=2024, race_name='Monaco')
print(f'Loaded {len(replay.laps_data)} total laps\n')

# Replay just laps 63-65 to see the failure point
print('Starting targeted replay (laps 63-65)...\n')
for lap in range(63, 66):
    print(f'{"="*60}')
    print(f'Pushing lap {lap}')
    print(f'{"="*60}')
    replay.push_lap_data(lap)
    print()

print('Replay complete')
