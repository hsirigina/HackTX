#!/bin/bash

echo ""
echo "🧪 QUICK DYNAMIC STRATEGY TEST"
echo "======================================================================"
echo ""
echo "This test will:"
echo "1. Wait for race replay to finish loading (if still running)"
echo "2. Run AI monitor to analyze the race"
echo "3. Show that recommendations are dynamic"
echo "4. Verify pit prediction accuracy"
echo ""

# Check if race data is loaded
echo "Step 1: Checking race data status..."
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
response = supabase.table('lap_times').select('lap_number').eq('race_id', 'bahrain_2024').execute()

if response.data and len(response.data) > 0:
    max_lap = max([r['lap_number'] for r in response.data])
    print(f'   ✅ Race data present: {max_lap} laps loaded')
    if max_lap >= 57:
        print('   ✅ Full race loaded!')
        exit(0)
    else:
        print(f'   ⏳ Still loading... ({max_lap}/57 laps)')
        exit(1)
else:
    print('   ❌ No race data yet - run race_replay.py first!')
    exit(1)
"

if [ $? -eq 1 ]; then
    echo ""
    echo "Waiting for race data to finish loading..."
    echo "(This may take 10-30 seconds)"
    sleep 10
fi

echo ""
echo "======================================================================"
echo "Step 2: Running AI Monitor..."
echo "======================================================================"
echo ""

python3 race_monitor_v2.py LEC bahrain_2024 2>&1 | head -200

echo ""
echo "======================================================================"
echo "Step 3: Testing Dynamic Recommendations..."
echo "======================================================================"
echo ""

python3 test_dynamic_strategy.py

echo ""
echo "======================================================================"
echo "Step 4: Analyzing Pit Prediction Accuracy..."
echo "======================================================================"
echo ""

python3 analyze_strategy_performance.py

echo ""
echo "======================================================================"
echo "✅ TEST COMPLETE!"
echo "======================================================================"
echo ""
