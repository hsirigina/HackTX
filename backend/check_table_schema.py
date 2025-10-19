"""Check the actual schema of agent_recommendations table"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('/Users/harsh/Documents/GitHub/HackTX/.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Try to insert a minimal record to see what's required
try:
    # First, let's see if there are any existing records
    result = supabase.table('agent_recommendations').select('*').limit(1).execute()

    if result.data and len(result.data) > 0:
        print('Existing record structure:')
        print(result.data[0])
        print('\nColumns:', list(result.data[0].keys()))
    else:
        print('No existing records found')

        # Try a minimal insert to see what fails
        print('\nAttempting minimal insert...')
        test_result = supabase.table('agent_recommendations').insert({
            'race_id': 'test',
            'driver': 'TEST',
            'lap_number': 1,
            'recommendation': {'test': 'data'}
        }).execute()

        print('Success! Minimal schema:')
        print(test_result.data[0])
        print('\nColumns:', list(test_result.data[0].keys()))

        # Clean up test record
        supabase.table('agent_recommendations').delete().eq('race_id', 'test').execute()

except Exception as e:
    print(f'Error: {e}')
