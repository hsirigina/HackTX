"""
FIXED Interactive Race Simulator
- 6 decision points (4 tactical, 2 pit stops)
- Fixed tire age tracking
- Fixed pit window logic
"""

from interactive_race_simulator import InteractiveRaceSimulator
from pit_window_selector import PitWindowSelector
from driving_style import DrivingStyle, DrivingStyleManager


def display_tactical_options(options, lap_number, description):
    """Display 3 tactical options"""
    print("\n" + "="*70)
    print(f"📍 LAP {lap_number} - {description}")
    print("="*70)

    for i, opt in enumerate(options, 1):
        emoji = {'HIGHLY_RECOMMENDED': '⭐', 'RECOMMENDED': '✅', 'ALTERNATIVE': '🔧'}[opt['confidence']]
        print(f"\n{emoji} OPTION {i}: {opt['title']}")
        print(f"   {opt['description']}")
        print(f"   Impact: {opt['impact']}")

    print("\n" + "="*70)


def get_user_choice():
    """Get 1, 2, or 3"""
    while True:
        try:
            choice = int(input("\n👉 Enter your choice (1-3): "))
            if 1 <= choice <= 3:
                return choice - 1
            print("❌ Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Please enter a number")
        except KeyboardInterrupt:
            print("\n\n🏁 Race abandoned!")
            exit()


def display_pit_window(window, current_lap):
    """Show pit window timeline"""
    print("\n" + "="*70)
    print(f"📍 LAP {current_lap} - PIT STOP DECISION")
    print("="*70)

    print(f"\n📊 CURRENT STATE:")
    print(f"   Tire: {window['current_state']['compound']}, {window['current_state']['tire_age']} laps old")
    print(f"   Tire cliff: Lap {window['current_state']['cliff_lap']} ({window['current_state']['laps_to_cliff']} laps away)")

    print(f"\n🎯 AI RECOMMENDATION:")
    print(f"   Pit on lap {window['optimal_lap']} for {window['optimal_compound']} tires")

    # Show visual timeline
    print(f"\n📅 PIT WINDOW TIMELINE:")
    timeline_str = ""
    for lap in window['lap_details'][:12]:
        emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}[lap.color]
        timeline_str += f"{emoji}{lap.lap_number} "

    print(f"   {timeline_str}")
    print(f"\n   🟢=OPTIMAL  🟡=OK  🔴=RISKY")
    print("\n" + "="*70)


def get_pit_lap(current_lap, max_lap, optimal_lap):
    """Get pit lap from user"""
    while True:
        try:
            print(f"👉 Enter lap number to pit (recommended: {optimal_lap}): ", end='')
            choice = input().strip()
            lap_num = int(choice)

            if lap_num <= current_lap:
                print(f"❌ Must be after current lap ({current_lap})")
                continue

            if lap_num > max_lap:
                print(f"❌ Race only has {max_lap} laps")
                continue

            return lap_num

        except ValueError:
            print("❌ Please enter a valid lap number")
        except KeyboardInterrupt:
            print("\n\n🏁 Race abandoned!")
            exit()


def run_fixed_race():
    """Run race with 6 decision points - FIXED VERSION"""

    print("="*70)
    print("🏎️  F1 INTERACTIVE RACE SIMULATOR")
    print("="*70)
    print("\n📋 GOAL: Beat Verstappen's Bahrain 2024 race time")
    print("📋 Make 6 strategic decisions:")
    print("   - 4 tactical decisions (3 options each)")
    print("   - 2 pit stops (type lap number)\n")

    input("Press ENTER to start the race... ")

    # Create simulator
    sim = InteractiveRaceSimulator(
        race_year=2024,
        race_name='Bahrain',
        total_laps=57,
        comparison_driver='VER',
        demo_mode=False
    )

    race_info = sim.start_race(starting_position=3, starting_compound='SOFT')
    print(f"\n🎯 TARGET: Beat {race_info['comparison_time']:.1f}s\n")

    selector = PitWindowSelector(sim.tire_model, sim.total_laps)

    # ========== DECISION 1: LAP 1 - DRIVING STYLE ==========
    options_lap1 = [
        {
            'title': 'AGGRESSIVE',
            'description': 'Push hard - faster laps but more tire wear',
            'impact': '-0.3s per lap, +40% tire wear',
            'confidence': 'RECOMMENDED',
            'style': DrivingStyle.AGGRESSIVE
        },
        {
            'title': 'BALANCED',
            'description': 'Standard race pace - manage tires and position',
            'impact': 'Baseline pace, normal tire wear',
            'confidence': 'HIGHLY_RECOMMENDED',
            'style': DrivingStyle.BALANCED
        },
        {
            'title': 'CONSERVATIVE',
            'description': 'Save tires - slower but extends stint',
            'impact': '+0.4s per lap, -30% tire wear',
            'confidence': 'ALTERNATIVE',
            'style': DrivingStyle.CONSERVATIVE
        }
    ]

    display_tactical_options(options_lap1, 1, "DRIVING STYLE")
    choice = get_user_choice()
    sim.state.driving_style = options_lap1[choice]['style']
    print(f"\n✅ Driving style: {options_lap1[choice]['title']}")

    # Update tire model
    style_mgr = DrivingStyleManager(sim.state.driving_style)
    sim.tire_model.driving_style_multiplier = style_mgr.get_tire_wear_multiplier()

    # Track state
    planned_pit_lap = None
    planned_pit_compound = None
    first_pit_done = False
    second_pit_done = False
    pit_windows_shown = 0

    # Simulate race lap by lap
    for current_lap in range(1, sim.total_laps + 1):
        # Check if we should pit this lap
        if planned_pit_lap == current_lap:
            print(f"\n⏩ LAP {current_lap} - PITTING FOR {planned_pit_compound} TIRES")

            # Execute pit
            sim.state.tire_compound = planned_pit_compound
            sim.state.tire_age = 0  # ✅ RESET TO ZERO
            sim.state.total_race_time += 25.0
            sim.state.pit_stops.append({
                'lap': current_lap,
                'compound': planned_pit_compound,
                'reason': 'User planned pit'
            })

            print(f"✅ Pitted for {planned_pit_compound} tires (+25.0s)")

            # Mark pit as done
            if not first_pit_done:
                first_pit_done = True
            else:
                second_pit_done = True

            # Clear planned pit
            planned_pit_lap = None
            planned_pit_compound = None

        # Simulate this lap
        # NOTE: simulate_lap() ALREADY increments tire_age internally!
        lap_time, _ = sim.simulate_lap(current_lap)
        sim.state.current_lap = current_lap + 1

        # ========== DECISION 2: LAP 10 - TACTICAL ==========
        if current_lap == 10:
            options_lap10 = [
                {
                    'title': 'PUSH HARD',
                    'description': 'Attack the cars ahead, build gap',
                    'impact': '-0.2s per lap, +20% tire wear for 10 laps',
                    'confidence': 'RECOMMENDED'
                },
                {
                    'title': 'MAINTAIN PACE',
                    'description': 'Hold current position and pace',
                    'impact': 'No change',
                    'confidence': 'HIGHLY_RECOMMENDED'
                },
                {
                    'title': 'CONSERVE TIRES',
                    'description': 'Back off slightly, save tires',
                    'impact': '+0.2s per lap, -20% tire wear for 10 laps',
                    'confidence': 'ALTERNATIVE'
                }
            ]

            display_tactical_options(options_lap10, 10, "TACTICAL ADJUSTMENT")
            choice = get_user_choice()
            print(f"\n✅ Tactic: {options_lap10[choice]['title']}")

        # ========== DECISION 3: FIRST PIT WINDOW (~70% tire) ==========
        max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
        tire_pct = sim.state.tire_age / max_laps

        if (tire_pct >= 0.70 and pit_windows_shown == 0 and
            planned_pit_lap is None and not first_pit_done):

            laps_remaining = sim.total_laps - current_lap

            window = selector.generate_pit_window(
                current_lap=current_lap,
                current_tire_age=sim.state.tire_age,
                current_compound=sim.state.tire_compound,
                laps_remaining=laps_remaining
            )

            display_pit_window(window, current_lap)
            planned_pit_lap = get_pit_lap(current_lap, sim.total_laps, window['optimal_lap'])
            planned_pit_compound = window['optimal_compound']

            print(f"\n✅ Planned: Pit lap {planned_pit_lap} for {planned_pit_compound} tires")
            pit_windows_shown += 1

        # ========== DECISION 4: LAP 30 - TACTICAL ==========
        if current_lap == 30:
            options_lap30 = [
                {
                    'title': 'ATTACK MODE',
                    'description': 'Close gap to leaders, aggressive pace',
                    'impact': '-0.3s per lap, +30% tire wear',
                    'confidence': 'RECOMMENDED'
                },
                {
                    'title': 'HOLD POSITION',
                    'description': 'Maintain current pace and position',
                    'impact': 'No change',
                    'confidence': 'HIGHLY_RECOMMENDED'
                },
                {
                    'title': 'MANAGE TIRES',
                    'description': 'Extend second stint, save tires',
                    'impact': '+0.3s per lap, -30% tire wear',
                    'confidence': 'ALTERNATIVE'
                }
            ]

            display_tactical_options(options_lap30, 30, "MID-RACE STRATEGY")
            choice = get_user_choice()
            print(f"\n✅ Strategy: {options_lap30[choice]['title']}")

        # ========== DECISION 5: SECOND PIT WINDOW (~70% tire on stint 2) ==========
        if (tire_pct >= 0.70 and pit_windows_shown == 1 and
            planned_pit_lap is None and first_pit_done and not second_pit_done):

            laps_remaining = sim.total_laps - current_lap

            # Only offer if enough laps left
            if laps_remaining > 10:
                window = selector.generate_pit_window(
                    current_lap=current_lap,
                    current_tire_age=sim.state.tire_age,
                    current_compound=sim.state.tire_compound,
                    laps_remaining=laps_remaining
                )

                display_pit_window(window, current_lap)
                planned_pit_lap = get_pit_lap(current_lap, sim.total_laps, window['optimal_lap'])
                planned_pit_compound = window['optimal_compound']

                print(f"\n✅ Planned: Pit lap {planned_pit_lap} for {planned_pit_compound} tires")
                pit_windows_shown += 1

        # ========== DECISION 6: LAP 55 - FINAL PUSH ==========
        if current_lap == 55:
            options_lap55 = [
                {
                    'title': 'QUALI MODE',
                    'description': 'All-out attack, maximum pace',
                    'impact': '-0.8s per lap, 200% tire wear (3 laps)',
                    'confidence': 'HIGHLY_RECOMMENDED'
                },
                {
                    'title': 'PUSH',
                    'description': 'Strong pace but manage to finish',
                    'impact': '-0.3s per lap, 120% tire wear',
                    'confidence': 'RECOMMENDED'
                },
                {
                    'title': 'BRING IT HOME',
                    'description': 'Ensure car finishes, no risks',
                    'impact': '+0.2s per lap, 80% tire wear',
                    'confidence': 'ALTERNATIVE'
                }
            ]

            display_tactical_options(options_lap55, 55, "FINAL LAPS")
            choice = get_user_choice()
            print(f"\n✅ Final strategy: {options_lap55[choice]['title']}")

        # Progress indicator
        if current_lap % 10 == 0 and current_lap not in [10, 30]:
            print(f"⏩ Lap {current_lap}/57 | Tire: {sim.state.tire_compound} {sim.state.tire_age} laps | Pits: {len(sim.state.pit_stops)}")

    # ========== FINAL RESULTS ==========
    final_comparison = sim.get_final_comparison()

    print("\n" + "="*70)
    print("🏁 RACE FINISHED!")
    print("="*70)

    print(f"\n🏆 YOUR RACE PERFORMANCE:")
    print(f"   Your time:        {final_comparison['user_time']:.1f}s")
    print(f"   Winner's time:    {final_comparison['full_leaderboard'][0]['time']:.1f}s ({final_comparison['full_leaderboard'][0]['driver']})")
    print(f"   Gap to winner:    +{final_comparison['gap_to_winner']:.1f}s")
    print(f"   Final position:   P{final_comparison['leaderboard_position']} / {final_comparison['total_drivers']}")

    # Show leaderboard
    print(f"\n📊 LEADERBOARD (Your Position):")
    print("="*70)
    for driver in final_comparison['nearby_drivers']:
        is_you = driver['driver'] == 'YOU'
        marker = '👉' if is_you else '  '
        print(f"{marker} {driver['driver']:3s}  {driver['team']:25s}  {driver['time']:.1f}s")

    print(f"\n📋 YOUR STRATEGY:")
    print(f"   Driving style: {sim.state.driving_style.value}")
    print(f"   Pit stops: {len(sim.state.pit_stops)}")
    for i, pit in enumerate(sim.state.pit_stops, 1):
        print(f"   Pit {i}: Lap {pit['lap']} → {pit['compound']} tires")

    print("\n" + "="*70)
    print("Thanks for racing! 🏎️")
    print("="*70)


if __name__ == '__main__':
    try:
        run_fixed_race()
    except KeyboardInterrupt:
        print("\n\n🏁 Race abandoned!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
