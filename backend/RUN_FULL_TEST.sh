#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "🧪 FULL DYNAMIC STRATEGY TEST"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This will:"
echo "1. Clear old data"
echo "2. Run Bahrain race replay (fast - 12 seconds)"
echo "3. Run AI race monitor (analyzes each lap)"
echo "4. Test that recommendations are dynamic"
echo "5. Analyze pit prediction accuracy"
echo ""
read -p "Press ENTER to start..."

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STEP 1: Clearing old Monaco data..."
echo "════════════════════════════════════════════════════════════════"

python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

tables = ['lap_times', 'tire_data', 'pit_stops', 'race_positions', 'agent_recommendations', 'agent_status']
for table in tables:
    try:
        supabase.table(table).delete().neq('race_id', 'bahrain_2024').execute()
        print(f'✓ Cleared {table}')
    except:
        pass

print('✅ Old data cleared')
"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STEP 2: Running race replay (Bahrain 2024)..."
echo "════════════════════════════════════════════════════════════════"
echo "This will take ~12 seconds (5 laps/second)"
echo ""

# Run race replay in background, capture PID
python3 race_replay.py &
REPLAY_PID=$!

# Wait for replay to finish
wait $REPLAY_PID

echo ""
echo "✅ Race replay complete!"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STEP 3: Running AI race monitor..."
echo "════════════════════════════════════════════════════════════════"
echo "AI will analyze all 57 laps from database"
echo ""

# Check if race monitor exists
if [ ! -f "race_monitor_v2.py" ]; then
    echo "❌ race_monitor_v2.py not found!"
    exit 1
fi

# Run race monitor
python3 race_monitor_v2.py LEC bahrain_2024

echo ""
echo "✅ AI analysis complete!"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STEP 4: Testing recommendation diversity..."
echo "════════════════════════════════════════════════════════════════"

python3 test_dynamic_strategy.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STEP 5: Analyzing pit prediction accuracy..."
echo "════════════════════════════════════════════════════════════════"

python3 analyze_strategy_performance.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ FULL TEST COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "If you saw:"
echo "  ✅ Multiple recommendation types (PIT_NOW, PIT_SOON, STAY_OUT)"
echo "  ✅ Different tactical instructions"
echo "  ✅ 100% pit prediction accuracy"
echo ""
echo "Then your system is FULLY DYNAMIC and working correctly!"
echo ""
