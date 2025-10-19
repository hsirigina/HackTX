"""
Analyze AI Strategy Performance vs Actual Race
Compares AI recommendations to what actually happened in the race
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def analyze_strategy(race_id='bahrain_2024', driver='LEC'):
    """Analyze how AI strategy performed vs actual race"""

    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    print(f"\n{'='*70}")
    print(f"🔍 AI STRATEGY ANALYSIS: {race_id.upper()} - {driver}")
    print(f"{'='*70}")

    # Get actual pit stops from race data
    print("\n📊 ACTUAL RACE PIT STOPS:")
    pit_response = supabase.table('pit_stops').select('*').eq(
        'race_id', race_id
    ).eq('driver_name', driver).order('lap_number').execute()

    actual_pits = []
    if pit_response.data:
        for pit in pit_response.data:
            lap = pit['lap_number']
            actual_pits.append(lap)
            print(f"   Lap {lap}: Pit stop ({pit.get('pit_duration_seconds', 25):.1f}s)")
    else:
        print("   No pit stops recorded")

    # Get AI recommendations
    print("\n🤖 AI RECOMMENDATIONS:")
    rec_response = supabase.table('agent_recommendations').select('*').eq(
        'race_id', race_id
    ).order('lap_number').execute()

    if not rec_response.data:
        print("   ⚠️  No recommendations found yet - run race_monitor_v2.py first!")
        return

    pit_now_laps = []
    pit_soon_laps = []

    for rec in rec_response.data:
        lap = rec['lap_number']
        rec_type = rec['recommendation_type']

        if rec_type == 'PIT_NOW':
            pit_now_laps.append(lap)
            print(f"   Lap {lap}: PIT_NOW - {rec['driver_instruction']}")
        elif rec_type == 'PIT_SOON':
            pit_soon_laps.append(lap)
            print(f"   Lap {lap}: PIT_SOON - {rec['driver_instruction']}")

    # Analysis
    print(f"\n{'='*70}")
    print("📈 STRATEGY COMPARISON:")
    print(f"{'='*70}")

    print(f"\nActual pit stops: {len(actual_pits)} times")
    if actual_pits:
        print(f"   Laps: {actual_pits}")

    print(f"\nAI 'PIT_NOW' recommendations: {len(pit_now_laps)} times")
    if pit_now_laps:
        print(f"   Laps: {pit_now_laps}")

    print(f"\nAI 'PIT_SOON' warnings: {len(pit_soon_laps)} times")
    if pit_soon_laps:
        print(f"   Laps: {pit_soon_laps[:5]}{'...' if len(pit_soon_laps) > 5 else ''}")

    # Check alignment
    print(f"\n{'='*70}")
    print("✅ ALIGNMENT CHECK:")
    print(f"{'='*70}")

    for actual_pit_lap in actual_pits:
        # Check if AI recommended pit within ±3 laps
        nearby_pit_now = [l for l in pit_now_laps if abs(l - actual_pit_lap) <= 3]
        nearby_pit_soon = [l for l in pit_soon_laps if abs(l - actual_pit_lap) <= 5]

        if nearby_pit_now:
            print(f"\n✅ Actual pit lap {actual_pit_lap}:")
            print(f"   AI said PIT_NOW on lap(s): {nearby_pit_now}")
            print(f"   🎯 MATCH! AI predicted within 3 laps")
        elif nearby_pit_soon:
            print(f"\n⚠️  Actual pit lap {actual_pit_lap}:")
            print(f"   AI said PIT_SOON on lap(s): {nearby_pit_soon}")
            print(f"   📊 Partial match (warned within 5 laps)")
        else:
            print(f"\n❌ Actual pit lap {actual_pit_lap}:")
            print(f"   AI did NOT predict this pit stop")

    # Check false positives
    print(f"\n{'='*70}")
    print("🔍 FALSE POSITIVES (AI recommended, but no actual pit):")
    print(f"{'='*70}")

    false_positives = []
    for ai_lap in pit_now_laps:
        if not any(abs(ai_lap - actual) <= 3 for actual in actual_pits):
            false_positives.append(ai_lap)

    if false_positives:
        print(f"\n   Laps {false_positives}")
        print("   ⚠️  AI suggested pitting but driver stayed out")
    else:
        print("\n   ✅ None - AI didn't recommend unnecessary pit stops!")

    # Overall verdict
    print(f"\n{'='*70}")
    print("🏁 FINAL VERDICT:")
    print(f"{'='*70}")

    if len(actual_pits) == 0:
        print("\n   No pit stops in race - nothing to validate")
    else:
        matches = sum(1 for pit in actual_pits if any(abs(l - pit) <= 3 for l in pit_now_laps))
        accuracy = (matches / len(actual_pits)) * 100 if actual_pits else 0

        print(f"\n   Actual pit stops: {len(actual_pits)}")
        print(f"   AI predictions (within 3 laps): {matches}/{len(actual_pits)}")
        print(f"   Accuracy: {accuracy:.0f}%")

        if accuracy >= 80:
            print("\n   ✅ EXCELLENT - AI strategy closely matches optimal race strategy!")
        elif accuracy >= 50:
            print("\n   📊 GOOD - AI strategy partially aligned with race strategy")
        else:
            print("\n   ⚠️  NEEDS TUNING - AI strategy diverges from actual race")

    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    analyze_strategy()
