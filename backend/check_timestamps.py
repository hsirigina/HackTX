from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('/Users/harsh/Documents/GitHub/HackTX/.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Check when data was created for lap 64
result = supabase.table('race_positions').select('driver_number, position, timestamp').eq('race_id', 'monaco_2024').eq('lap_number', 64).order('timestamp').execute()

print(f'Lap 64 - Total records: {len(result.data)}\n')
if result.data:
    for idx, record in enumerate(result.data, 1):
        print(f'{idx}. Driver #{record["driver_number"]:2d} - P{record["position"]:2d} - {record["timestamp"]}')
