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
            'ALTERNATIVE': '🔧'
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


def run_interactive_race():
    """Run full interactive race simulation"""

    print("="*70)
    print("🏎️  F1 INTERACTIVE RACE SIMULATOR")
    print("="*70)
    print("\n📋 GOAL: Beat Verstappen's Bahrain 2024 race time")
    print("📋 You'll make strategic decisions throughout the race")
    print("📋 Choose wisely - every decision affects your final time!\n")

    input("Press ENTER to start the race... ")

    # Create simulator
    sim = InteractiveRaceSimulator(
        race_year=2024,
        race_name='Bahrain',
        total_laps=57,
        comparison_driver='VER'
    )

    # Start race
    race_info = sim.start_race(starting_position=3, starting_compound='SOFT')

    print(f"\n🎯 TARGET: Beat {race_info['comparison_time']:.1f}s")

    # Race through all decision points
    for decision_lap in sim.decision_laps:
        # Simulate laps until decision point
        if sim.state.current_lap < decision_lap:
            print(f"\n⏩ Fast-forwarding to lap {decision_lap}...")
            while sim.state.current_lap < decision_lap:
                lap_time, lap_info = sim.simulate_lap(sim.state.current_lap)
                sim.state.current_lap += 1

            # Show current state
            print(f"\n📍 LAP {decision_lap}")
            print(f"   Current position: P{sim.state.position}")
            print(f"   Tire: {sim.state.tire_compound}, {sim.state.tire_age} laps old")
            print(f"   Driving style: {sim.state.driving_style.value}")
            print(f"   Total race time: {sim.state.total_race_time:.1f}s")
            print(f"   Pit stops: {len(sim.state.pit_stops)}")

        # Generate decision options
        options = sim.generate_decision_options(decision_lap)

        if not options:
            continue

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

    # Simulate remaining laps to finish
    print(f"\n⏩ Racing to the finish...")
    while sim.state.current_lap < sim.total_laps:
        lap_time, lap_info = sim.simulate_lap(sim.state.current_lap)
        sim.state.current_lap += 1

    # Final lap
    lap_time, lap_info = sim.simulate_lap(sim.total_laps)

    # Show final results
    final_comparison = sim.get_final_comparison()

    print("\n" + "="*70)
    print("🏁 RACE FINISHED!")
    print("="*70)

    print(f"\n🏆 RESULTS:")
    print(f"   Your time:        {final_comparison['user_time']:.1f}s")
    print(f"   {final_comparison['comparison_driver']}'s time:     {final_comparison['comparison_time']:.1f}s")
    print(f"   Difference:       {final_comparison['time_delta']:+.1f}s")

    if final_comparison['result'] == 'WON':
        print(f"\n🎉 YOU WON! You beat {final_comparison['comparison_driver']} by {abs(final_comparison['time_delta']):.1f} seconds!")
    else:
        print(f"\n😔 You lost by {final_comparison['time_delta']:.1f} seconds. Better luck next time!")

    print(f"\n📊 RACE SUMMARY:")
    print(f"   Pit stops: {final_comparison['pit_stops']}")
    print(f"   Decisions made: {final_comparison['decisions_made']}")

    print(f"\n📋 DECISION TIMELINE:")
    for decision in final_comparison['decision_timeline']:
        print(f"   Lap {decision['lap']:2d}: {decision['title']}")

    print("\n" + "="*70)
    print("Thanks for racing! 🏎️")
    print("="*70)


if __name__ == '__main__':
    try:
        run_interactive_race()
    except KeyboardInterrupt:
        print("\n\n🏁 Race abandoned!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
