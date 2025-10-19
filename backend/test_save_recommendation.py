"""Test saving recommendation with new schema"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('/Users/harsh/Documents/GitHub/HackTX/.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Test saving a recommendation with the correct schema
test_rec = {
    'race_id': 'test_monaco',
    'lap_number': 99,
    'agent_name': 'COORDINATOR',
    'recommendation_type': 'PIT_SOON',
    'confidence_score': 0.85,
    'reasoning': 'Test reasoning - tire degradation detected'
}

try:
    result = supabase.table('agent_recommendations').insert(test_rec).execute()
    print('✅ Save successful!')
    print('Saved record:', result.data[0])

    # Clean up
    supabase.table('agent_recommendations').delete().eq('race_id', 'test_monaco').execute()
    print('\n✅ Test record cleaned up')

except Exception as e:
    print(f'❌ Save failed: {e}')
