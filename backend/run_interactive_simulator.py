"""
Run the interactive race simulator with user input
User makes decisions, races against Verstappen's actual time
"""

from interactive_race_simulator import InteractiveRaceSimulator
import time


def display_options(options):
    """Display decision options to user"""
    print("\n" + "="*70)
    print("🎯 YOUR OPTIONS:")
    print("="*70)

    for i, option in enumerate(options, 1):
        confidence_emoji = {
            'HIGHLY_RECOMMENDED': '⭐',
            'RECOMMENDED': '✅',
            'ALTERNATIVE': '🔧',
            'NOT_RECOMMENDED': '❌'
        }.get(option.ai_confidence, '❓')

        print(f"\n{confidence_emoji} OPTION {i}: {option.title}")
        print(f"   {option.description}")
        print(f"   💭 Reasoning: {option.reasoning}")
        print(f"   📊 Race time impact: {option.predicted_race_time_impact:+.1f}s")
        print(f"   ⏱️  Lap time impact: {option.predicted_lap_time_impact:+.1f}s")
        print(f"   🔥 Tire wear: {option.tire_wear_impact:.1f}x")
        print(f"   ✅ Pros: {', '.join(option.pros)}")
        print(f"   ❌ Cons: {', '.join(option.cons)}")
        print(f"   🤖 AI Confidence: {option.ai_confidence}")


def get_user_choice(num_options):
    """Get user's choice (1, 2, or 3)"""
    while True:
        try:
            choice = input(f"\n👉 Enter your choice (1-{num_options}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= num_options:
                return choice_num - 1  # Convert to 0-indexed
            else:
                print(f"❌ Please enter a number between 1 and {num_options}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n🏁 Race abandoned!")
            exit()


def run_interactive_race(demo_mode=False):
    """Run full interactive race simulation"""

    print("="*70)
    print("🏎️  F1 INTERACTIVE RACE SIMULATOR")
    print("="*70)

    if demo_mode:
        print("\n🎮 DEMO MODE: Quick race with only critical decisions (~5-8 total)")
    else:
        print("\n🎮 FULL MODE: Detailed race with all strategic decisions (~25 total)")

    print("\n📋 GOAL: Beat Verstappen's Bahrain 2024 race time")
    print("📋 You'll make strategic decisions throughout the race")
    print("📋 Choose wisely - every decision affects your final time!\n")

    input("Press ENTER to start the race... ")

    # Create simulator
    sim = InteractiveRaceSimulator(
        race_year=2024,
        race_name='Bahrain',
        total_laps=57,
        comparison_driver='VER',
        demo_mode=demo_mode
    )

    # Start race
    race_info = sim.start_race(starting_position=3, starting_compound='SOFT')

    print(f"\n🎯 TARGET: Beat {race_info['comparison_time']:.1f}s")

    # Race through ALL laps - check each one if decision needed (DYNAMIC!)
    current_lap = 1
    while current_lap <= sim.total_laps:
        # Check if we should offer decision at this lap
        if sim.should_offer_decision(current_lap):
            # Show current state
            print(f"\n📍 LAP {current_lap}")
            print(f"   Current position: P{sim.state.position}")
            print(f"   Tire: {sim.state.tire_compound}, {sim.state.tire_age} laps old")
            print(f"   Driving style: {sim.state.driving_style.value}")
            print(f"   Total race time: {sim.state.total_race_time:.1f}s")
            print(f"   Pit stops: {len(sim.state.pit_stops)}")

            # Generate decision options
            options = sim.generate_decision_options(current_lap)

            if not options:
                print(f"   ⚠️  No decision options at this lap (cruising)")
                current_lap += 1
                continue

            # Show WHY this decision point was triggered
            max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
            tire_pct = (sim.state.tire_age / max_laps) * 100
            print(f"\n🔍 DECISION TRIGGER:")
            print(f"   Tire age: {sim.state.tire_age}/{max_laps} laps ({tire_pct:.0f}%)")
            print(f"   Compound: {sim.state.tire_compound}")
            print(f"   Approaching cliff: {'YES ⚠️' if sim.state.tire_age >= (max_laps * 0.70) else 'No'}")
            print(f"   Past cliff: {'YES 🔴' if sim.state.tire_age >= max_laps else 'No'}")

            # Count recommendations
            recommended_count = sum(1 for opt in options if opt.ai_confidence in ['HIGHLY_RECOMMENDED', 'RECOMMENDED'])
            print(f"\n📊 RECOMMENDATION SUMMARY:")
            print(f"   {sum(1 for opt in options if opt.ai_confidence == 'HIGHLY_RECOMMENDED')} Highly Recommended")
            print(f"   {sum(1 for opt in options if opt.ai_confidence == 'RECOMMENDED')} Recommended")
            print(f"   {sum(1 for opt in options if opt.ai_confidence == 'ALTERNATIVE')} Alternative")
            print(f"   {sum(1 for opt in options if opt.ai_confidence == 'NOT_RECOMMENDED')} Not Recommended")

            if recommended_count == 0:
                print(f"   ⚠️  WARNING: No recommended options! All alternatives!")

            # Display options
            display_options(options)

            # Get user choice
            choice_idx = get_user_choice(len(options))
            selected_option = options[choice_idx]

            # Execute decision
            result = sim.execute_decision(selected_option)

            print(f"\n{'='*70}")
            print(f"✅ DECISION EXECUTED")
            print(f"{'='*70}")
            print(f"   {result['message']}")

            # Pause for effect
            time.sleep(1)

        # Simulate this lap and move to next
        if sim.state.current_lap == current_lap:
            lap_time, lap_info = sim.simulate_lap(current_lap)
            sim.state.current_lap += 1

        current_lap += 1

    # Show final results
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

    # Show full top 10
    print(f"\n🏁 FULL TOP 10:")
    print("="*70)
    for i, driver in enumerate(final_comparison['full_leaderboard'], 1):
        is_you = driver['driver'] == 'YOU'
        marker = '👉' if is_you else f'P{i}'
        print(f"{marker:3s} {driver['driver']:3s}  {driver['team']:25s}  {driver['time']:.1f}s")

    print(f"\n📋 YOUR STRATEGY:")
    print(f"   Pit stops: {final_comparison['pit_stops']}")
    for i, pit in enumerate(final_comparison['pit_stop_details'], 1):
        print(f"   Pit {i}: Lap {pit['lap']} → {pit['compound']} tires")

    print(f"\n📋 DECISION TIMELINE:")
    for decision in final_comparison['decision_timeline']:
        print(f"   Lap {decision['lap']:2d}: {decision['title']}")

    print("\n" + "="*70)
    print("Thanks for racing! 🏎️")
    print("="*70)


if __name__ == '__main__':
    import sys

    # Check for --demo flag
    demo_mode = '--demo' in sys.argv

    try:
        run_interactive_race(demo_mode=demo_mode)
    except KeyboardInterrupt:
        print("\n\n🏁 Race abandoned!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
