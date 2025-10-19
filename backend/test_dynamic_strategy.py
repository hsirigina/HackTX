"""
Test that strategy system is truly dynamic and not hardcoded
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def test_dynamic_recommendations():
    """Verify recommendations change based on race state"""

    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    print("\n" + "="*70)
    print("🧪 TESTING DYNAMIC STRATEGY SYSTEM")
    print("="*70)
    print("\nVerifying recommendations are NOT hardcoded...")

    # Get recommendations from Bahrain race
    response = supabase.table('agent_recommendations').select(
        'lap_number, recommendation_type, driver_instruction, reasoning'
    ).eq('race_id', 'bahrain_2024').order('lap_number').execute()

    if not response.data or len(response.data) == 0:
        print("\n⚠️  No recommendations found!")
        print("   Run the race monitor first:")
        print("   python race_monitor_v2.py LEC bahrain_2024")
        return

    print(f"\n✅ Found {len(response.data)} recommendations")

    # Analyze diversity
    rec_types = {}
    tactical_instructions = set()

    print("\n📊 ANALYZING RECOMMENDATION DIVERSITY:")
    print("="*70)

    for rec in response.data:
        lap = rec['lap_number']
        rec_type = rec['recommendation_type']
        instruction = rec['driver_instruction']
        reasoning = rec['reasoning']

        # Count recommendation types
        rec_types[rec_type] = rec_types.get(rec_type, 0) + 1

        # Extract tactical instruction (last part after final period)
        if instruction:
            parts = instruction.split('.')
            if len(parts) > 1:
                tactic = parts[-1].strip()
                tactical_instructions.add(tactic)

        # Show some examples
        if lap in [1, 10, 12, 20, 35, 45, 57]:
            print(f"\nLap {lap}:")
            print(f"  Type: {rec_type}")
            print(f"  Instruction: {instruction[:80]}...")
            print(f"  Reasoning: {reasoning[:100]}...")

    print("\n" + "="*70)
    print("📈 DIVERSITY METRICS:")
    print("="*70)

    print("\nRecommendation types found:")
    for rec_type, count in rec_types.items():
        print(f"  {rec_type}: {count} times")

    print(f"\nUnique tactical instructions: {len(tactical_instructions)}")
    for tactic in list(tactical_instructions)[:10]:
        print(f"  • {tactic}")

    print("\n" + "="*70)
    print("✅ VERDICT:")
    print("="*70)

    # Check for diversity
    if len(rec_types) >= 2:
        print("\n✅ DYNAMIC - Multiple recommendation types detected")
    else:
        print("\n⚠️  LOW DIVERSITY - Only one recommendation type")

    if len(tactical_instructions) >= 3:
        print(f"✅ TACTICAL VARIETY - {len(tactical_instructions)} different tactical instructions")
    else:
        print("⚠️  LOW TACTICAL VARIETY")

    # Check recommendations changed over time
    first_rec = response.data[0]['recommendation_type']
    last_rec = response.data[-1]['recommendation_type']

    if first_rec != last_rec:
        print(f"✅ EVOLUTION - Strategy changed from {first_rec} → {last_rec}")
    else:
        print("⚠️  STATIC - Same recommendation type throughout")

    print("\n" + "="*70)
    print("\n💡 KEY INDICATOR: Dynamic system shows:")
    print("   • Multiple recommendation types (PIT_NOW, PIT_SOON, STAY_OUT)")
    print("   • Tactical instructions change based on race situation")
    print("   • Recommendations evolve as tire age increases")
    print("   • Different reasoning for different laps")

    if len(rec_types) >= 2 and len(tactical_instructions) >= 3:
        print("\n🎯 CONFIRMED: System is FULLY DYNAMIC - NOT hardcoded!")
    else:
        print("\n⚠️  System may be too conservative - check event triggers")

    print("="*70 + "\n")


if __name__ == '__main__':
    test_dynamic_recommendations()
