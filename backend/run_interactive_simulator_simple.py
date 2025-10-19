"""
Simple Interactive Race Simulator - Lap Number Input
User just types which lap to pit (no complex options)
"""

from interactive_race_simulator import InteractiveRaceSimulator
from pit_window_selector import PitWindowSelector
import sys


def display_pit_window(window, current_lap):
    """Show pit window with visual timeline"""
    print("\n" + "="*70)
    print("⏱️  PIT STOP DECISION")
    print("="*70)

    print(f"\n📊 CURRENT STATE:")
    print(f"   Lap: {window['current_state']['lap']}")
    print(f"   Tire: {window['current_state']['compound']}, {window['current_state']['tire_age']} laps old")
    print(f"   Tire cliff at lap {window['current_state']['cliff_lap']} ({window['current_state']['laps_to_cliff']} laps away)")

    print(f"\n🎯 AI RECOMMENDATION:")
    print(f"   Pit on lap {window['optimal_lap']} for {window['optimal_compound']} tires")
    print(f"   (Race time impact: {window['optimal_impact']:+.1f}s)")

    # Show visual timeline
    print(f"\n📅 PIT WINDOW TIMELINE:")
    print("="*70)

    # Group laps by color/recommendation
    timeline = []
    for lap in window['lap_details'][:15]:  # Show next 15 laps
        emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}[lap.color]
        timeline.append(f"{emoji} Lap {lap.lap_number}")

    # Print timeline in rows of 5
    for i in range(0, len(timeline), 5):
        print("   " + "  ".join(timeline[i:i+5]))

    print(f"\n   🟢 = RECOMMENDED  🟡 = ACCEPTABLE  🔴 = RISKY")

    # Show never pit warning if applicable
    if not window['never_pit']['possible']:
        print(f"\n   ⚠️  NEVER PIT: {window['never_pit']['warning']}")

    print("\n" + "="*70)


def get_pit_lap(current_lap, max_lap, optimal_lap):
    """Get pit lap from user (just a number)"""
    while True:
        try:
            print(f"\n👉 Enter lap number to pit (recommended: {optimal_lap}, or type 'never'): ", end='')
            choice = input().strip().lower()

            if choice == 'never' or choice == 'n':
                return None  # Never pit

            lap_num = int(choice)

            if lap_num <= current_lap:
                print(f"❌ Must be after current lap ({current_lap})")
                continue

            if lap_num > max_lap:
                print(f"❌ Race only has {max_lap} laps")
                continue

            return lap_num

        except ValueError:
            print("❌ Please enter a valid lap number or 'never'")
        except KeyboardInterrupt:
            print("\n\n🏁 Race abandoned!")
            exit()


def run_simple_race(demo_mode=True):
    """Run race with simple lap number input"""

    print("="*70)
    print("🏎️  F1 INTERACTIVE RACE SIMULATOR - SIMPLE MODE")
    print("="*70)
    print("\n📋 GOAL: Beat Verstappen's Bahrain 2024 race time")
    print("📋 You'll choose WHICH LAP to pit (just type a number!)")
    print("📋 AI will recommend optimal timing\n")

    input("Press ENTER to start the race... ")

    # Create simulator
    sim = InteractiveRaceSimulator(
        race_year=2024,
        race_name='Bahrain',
        total_laps=57,
        comparison_driver='VER',
        demo_mode=False  # We'll control decisions manually
    )

    # Start race
    race_info = sim.start_race(starting_position=3, starting_compound='SOFT')

    print(f"\n🎯 TARGET: Beat {race_info['comparison_time']:.1f}s")

    # Lap 1: Choose driving style
    print("\n📍 LAP 1 - CHOOSE DRIVING STYLE")
    print("="*70)
    print("\n1. AGGRESSIVE (faster, more tire wear)")
    print("2. BALANCED (standard pace)")
    print("3. CONSERVATIVE (slower, less tire wear)")

    while True:
        try:
            style_choice = int(input("\n👉 Enter your choice (1-3): "))
            if 1 <= style_choice <= 3:
                break
            print("❌ Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Please enter a number")

    # Map choice to style
    from driving_style import DrivingStyle
    styles = [DrivingStyle.AGGRESSIVE, DrivingStyle.BALANCED, DrivingStyle.CONSERVATIVE]
    sim.state.driving_style = styles[style_choice - 1]

    print(f"\n✅ Driving style set to {sim.state.driving_style.value}")

    # Create pit window selector
    selector = PitWindowSelector(sim.tire_model, sim.total_laps)

    # Track pit stops we need to make
    planned_pit_laps = []
    pit_compounds = []
    current_lap = 1

    # Simulate lap by lap
    while current_lap <= sim.total_laps:
        # Check if user planned to pit this lap
        if current_lap in planned_pit_laps:
            pit_index = planned_pit_laps.index(current_lap)
            compound = pit_compounds[pit_index]

            print(f"\n📍 LAP {current_lap} - PITTING FOR {compound} TIRES")

            # Execute pit stop
            sim.state.tire_compound = compound
            sim.state.tire_age = 1
            sim.state.total_race_time += 25.0  # Pit stop time
            sim.state.pit_stops.append({
                'lap': current_lap,
                'compound': compound,
                'reason': 'User planned pit stop'
            })

            print(f"✅ Pitted for {compound} tires (+25.0s)")

        # Simulate this lap
        lap_time, lap_info = sim.simulate_lap(current_lap)
        sim.state.current_lap = current_lap + 1

        # Check if we should offer pit decision
        # Only offer when tire is 70%+ worn and we don't have a pit planned soon
        max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
        tire_pct = sim.state.tire_age / max_laps

        # Skip if already planned a pit in next 5 laps
        has_upcoming_pit = any(current_lap < lap <= current_lap + 5 for lap in planned_pit_laps)

        if tire_pct >= 0.70 and not has_upcoming_pit and len(planned_pit_laps) < 3:
            # Offer pit window
            laps_remaining = sim.total_laps - current_lap

            window = selector.generate_pit_window(
                current_lap=current_lap,
                current_tire_age=sim.state.tire_age,
                current_compound=sim.state.tire_compound,
                laps_remaining=laps_remaining
            )

            # Display pit window
            display_pit_window(window, current_lap)

            # Get user's choice
            pit_lap = get_pit_lap(current_lap, sim.total_laps, window['optimal_lap'])

            if pit_lap:
                planned_pit_laps.append(pit_lap)
                pit_compounds.append(window['optimal_compound'])
                print(f"\n✅ Planned: Pit on lap {pit_lap} for {window['optimal_compound']} tires")
            else:
                print(f"\n✅ Planned: Never pit again (run to end on {sim.state.tire_compound} tires)")

        # Progress indicator every 10 laps
        if current_lap % 10 == 0 and current_lap not in planned_pit_laps:
            print(f"\n⏩ Lap {current_lap}/57 | Tire: {sim.state.tire_compound} {sim.state.tire_age} laps | Time: {sim.state.total_race_time:.1f}s")

        current_lap += 1

    # Final results
    final_comparison = sim.get_final_comparison()

    print("\n" + "="*70)
    print("🏁 RACE FINISHED!")
    print("="*70)

    print(f"\n🏆 YOUR RACE PERFORMANCE:")
    print(f"   Your time:        {final_comparison['user_time']:.1f}s")
    print(f"   Winner's time:    {final_comparison['full_leaderboard'][0]['time']:.1f}s ({final_comparison['full_leaderboard'][0]['driver']})")
    print(f"   Gap to winner:    +{final_comparison['gap_to_winner']:.1f}s")
    print(f"   Final position:   P{final_comparison['leaderboard_position']} / {final_comparison['total_drivers']}")

    # Show leaderboard around user
    print(f"\n📊 LEADERBOARD (Your Position):")
    print("="*70)
    for driver in final_comparison['nearby_drivers']:
        is_you = driver['driver'] == 'YOU'
        marker = '👉' if is_you else '  '
        print(f"{marker} {driver['driver']:3s}  {driver['team']:25s}  {driver['time']:.1f}s")

    print(f"\n📋 YOUR STRATEGY:")
    print(f"   Pit stops: {final_comparison['pit_stops']}")
    for i, pit in enumerate(final_comparison['pit_stop_details'], 1):
        print(f"   Pit {i}: Lap {pit['lap']} → {pit['compound']} tires")

    print("\n" + "="*70)
    print("Thanks for racing! 🏎️")
    print("="*70)


if __name__ == '__main__':
    try:
        run_simple_race(demo_mode=True)
    except KeyboardInterrupt:
        print("\n\n🏁 Race abandoned!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
