from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('/Users/harsh/Documents/GitHub/HackTX/.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Check multiple laps
for lap_num in [63, 64, 65]:
    result = supabase.table('race_positions').select('driver_number, position').eq('race_id', 'monaco_2024').eq('lap_number', lap_num).execute()
    print(f'Lap {lap_num}: {len(result.data)} drivers')
    if len(result.data) > 0:
        print(f'  Positions: {sorted([r["position"] for r in result.data])}')
