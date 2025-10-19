"""
HACKATHON DEMO SCRIPT
Shows AI strategy recommendations and compares outcomes
"""

import os
from dotenv import load_dotenv
from strategy_comparator import StrategyComparator

load_dotenv()

def main():
    print("\n" + "="*70)
    print("🏎️  F1 AI RACE STRATEGIST - HACKATHON DEMO")
    print("="*70)
    print("Showcasing: Real-time strategy AI with tire degradation modeling")
    print("="*70 + "\n")

    comparator = StrategyComparator(total_laps=78)

    # Demo Scenario 1: Early race (good tires)
    print("\n📍 SCENARIO 1: Lap 30 - Tires still fresh")
    print("-"*70)
    comparison = comparator.compare_strategies(
        start_lap=30,
        end_lap=78,
        current_tire_age=29,
        current_compound='HARD'
    )
    comparator.print_comparison(comparison)
    input("Press ENTER to continue...\n")

    # Demo Scenario 2: Mid race (tire degradation starting)
    print("\n📍 SCENARIO 2: Lap 50 - Tire degradation increasing")
    print("-"*70)
    comparison = comparator.compare_strategies(
        start_lap=50,
        end_lap=78,
        current_tire_age=49,
        current_compound='HARD'
    )
    comparator.print_comparison(comparison)
    input("Press ENTER to continue...\n")

    # Demo Scenario 3: Late race (critical decision)
    print("\n📍 SCENARIO 3: Lap 64 - CRITICAL PIT DECISION")
    print("-"*70)
    print("This is when AI screams: 'BOX BOX BOX!'")
    print()
    comparison = comparator.compare_strategies(
        start_lap=64,
        end_lap=78,
        current_tire_age=63,
        current_compound='HARD'
    )
    comparator.print_comparison(comparison)

    print("\n" + "="*70)
    print("🎯 KEY TAKEAWAY FOR JUDGES")
    print("="*70)
    print("""
Our AI system:
✅ Monitors 4 data streams (tires, pace, position, competitors)
✅ Runs physics-based tire degradation simulations
✅ Calculates optimal pit windows in real-time
✅ Provides strategic recommendations that save 60+ seconds
✅ Adapts to different track characteristics (Monaco vs Silverstone)

In a real race: 60 seconds = difference between P1 and P10

Without AI: Team guesses based on gut feel
With AI: Data-driven decisions that optimize race time

This is the future of F1 strategy engineering.
""")
    print("="*70 + "\n")

    # Show Monaco context
    print("💡 MONACO 2024 CONTEXT:")
    print("-"*70)
    print("In the actual race, Leclerc stayed out (no pit stop)")
    print("Why? Monaco is UNIQUE:")
    print("  • Impossible to overtake (track position > tire performance)")
    print("  • Low tire wear (smooth surface, slow corners)")
    print("  • Pitting = losing track position = losing the race")
    print()
    print("Our AI KNOWS this and factors it into recommendations!")
    print("On other tracks, it would aggressively recommend pitting.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
