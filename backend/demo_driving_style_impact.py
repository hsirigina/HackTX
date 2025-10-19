"""
Demo: How Driving Style Changes Strategy

Shows engineer how changing driving style affects:
- Tire wear rate
- Pit window timing
- Lap times
- Race outcome
"""

from tire_model import TireDegradationModel
from driving_style import DrivingStyleManager, DrivingStyle

def demo_style_impact():
    """
    Compare pit strategies under different driving styles
    """

    print("\n" + "="*70)
    print("🎮 DRIVING STYLE IMPACT ON RACE STRATEGY")
    print("="*70)
    print("\nScenario: Bahrain GP, Lap 10, HARD tires, 47 laps remaining")
    print("Question: When should we pit?\n")

    current_lap = 10
    tire_age = 9
    compound = 'HARD'

    styles_to_test = [
        (DrivingStyle.AGGRESSIVE, "Push hard - trying to undercut"),
        (DrivingStyle.BALANCED, "Normal race pace"),
        (DrivingStyle.CONSERVATIVE, "Saving tires for long stint")
    ]

    print("="*70)

    for style, description in styles_to_test:
        print(f"\n🎮 {style.value} ({description})")
        print("-"*70)

        # Get style parameters
        style_manager = DrivingStyleManager(style)
        wear_mult = style_manager.get_tire_wear_multiplier()
        lap_delta = style_manager.get_lap_time_adjustment()

        # Create tire model with this style
        tire_model = TireDegradationModel(
            total_laps=57,
            driving_style_multiplier=wear_mult
        )

        # Calculate optimal pit window
        scenarios = tire_model.optimal_pit_window(
            current_lap=current_lap,
            stint1_compound=compound,
            stint2_compound='MEDIUM'
        )

        optimal = scenarios[0]

        print(f"   Tire wear multiplier: {wear_mult}x")
        print(f"   Lap time adjustment: {lap_delta:+.1f}s per lap")
        print(f"   📍 Optimal pit lap: {optimal['pit_lap']}")
        print(f"   ⏱️  Total race time: {optimal['total_race_time']:.1f}s")

        # Calculate when to pit from current lap
        laps_to_pit = optimal['pit_lap'] - current_lap
        print(f"   👉 RECOMMENDATION: Pit in {laps_to_pit} laps")

        # Show tire degradation timeline
        print(f"\n   Tire degradation timeline:")
        for check_lap in [current_lap, current_lap+5, current_lap+10, optimal['pit_lap']]:
            if check_lap <= 57:
                check_age = tire_age + (check_lap - current_lap)
                laptime = tire_model.calculate_laptime(check_lap, check_age, compound)
                print(f"     Lap {check_lap} (age {check_age}): {laptime:.2f}s")

    print("\n" + "="*70)
    print("🎯 KEY INSIGHTS:")
    print("="*70)

    print("""
1. AGGRESSIVE driving:
   - Faster laps NOW (+0.3s/lap faster)
   - But tires degrade 40% faster
   - Forces EARLIER pit stop
   - Good for: Undercut attacks, defending position

2. CONSERVATIVE driving:
   - Slower laps NOW (-0.4s/lap slower)
   - But tires last 30% longer
   - Allows LATER pit stop (or no pit!)
   - Good for: Tire saving, track position secure

3. BALANCED driving:
   - Standard pace and wear
   - Predictable strategy
   - Good for: Normal racing conditions

🎮 Engineer Control: YOU choose the style based on race situation!
""")

    print("="*70 + "\n")


def demo_live_style_change():
    """
    Demo changing style mid-race based on race situation
    """

    print("\n" + "="*70)
    print("📡 LIVE DRIVING STYLE CHANGES DURING RACE")
    print("="*70)

    manager = DrivingStyleManager(DrivingStyle.BALANCED)

    print("\nSimulating race with style changes based on competition:")
    print("-"*70)

    race_scenarios = [
        (10, DrivingStyle.BALANCED, "Clear air - manage pace", None, None),
        (20, DrivingStyle.AGGRESSIVE, "Car ahead 2.5s - undercut attempt", 2.5, 5.0),
        (22, DrivingStyle.BALANCED, "Undercut successful - back to normal", 5.0, 3.0),
        (35, DrivingStyle.CONSERVATIVE, "Second stint - tire saving", 8.0, 4.0),
        (54, DrivingStyle.QUALI_MODE, "Final laps - 1.2s behind leader!", 1.2, None),
    ]

    for lap, style, reason, gap_ahead, gap_behind in race_scenarios:
        print(f"\n📍 LAP {lap}:")
        print(f"   Situation: {reason}")
        if gap_ahead:
            print(f"   Gap ahead: {gap_ahead}s")
        if gap_behind:
            print(f"   Gap behind: {gap_behind}s")

        # Change style
        manager.set_style(style, lap, reason)

        # Show impact
        profile = manager.get_current_profile()
        print(f"   → Lap time: {profile['lap_time_delta']:+.1f}s")
        print(f"   → Tire wear: {profile['tire_wear_multiplier']}x")
        print(f"   → Risk level: {profile['risk_level']}")

    print("\n" + "="*70)
    print("📊 STYLE CHANGE HISTORY:")
    print("="*70)

    for change in manager.style_history:
        print(f"\nLap {change['lap']}: {change['from_style'].value} → {change['to_style'].value}")
        print(f"  Reason: {change['reason']}")
        print(f"  Duration in previous style: {change['laps_in_previous']} laps")

    print("\n" + "="*70 + "\n")


def demo_ai_style_recommendations():
    """
    Show how AI recommends driving styles based on race state
    """

    print("\n" + "="*70)
    print("🤖 AI DRIVING STYLE RECOMMENDATIONS")
    print("="*70)

    manager = DrivingStyleManager()

    test_scenarios = [
        {
            'name': 'Undercut Opportunity',
            'tire_age': 8,
            'laps_remaining': 42,
            'gap_ahead': 2.3,
            'gap_behind': 6.0
        },
        {
            'name': 'Under Pressure',
            'tire_age': 15,
            'laps_remaining': 30,
            'gap_ahead': 8.0,
            'gap_behind': 1.5
        },
        {
            'name': 'Old Tires',
            'tire_age': 38,
            'laps_remaining': 15,
            'gap_ahead': 5.0,
            'gap_behind': 7.0
        },
        {
            'name': 'Final Lap Battle',
            'tire_age': 20,
            'laps_remaining': 1,
            'gap_ahead': 0.8,
            'gap_behind': None
        }
    ]

    for scenario in test_scenarios:
        print(f"\n📊 {scenario['name']}:")
        print(f"   Tire age: {scenario['tire_age']} laps")
        print(f"   Laps remaining: {scenario['laps_remaining']}")
        print(f"   Gap ahead: {scenario['gap_ahead']}s" if scenario['gap_ahead'] else "   Gap ahead: None")
        print(f"   Gap behind: {scenario['gap_behind']}s" if scenario['gap_behind'] else "   Gap behind: None")

        rec = manager.recommend_style(
            current_situation={},
            tire_age=scenario['tire_age'],
            laps_remaining=scenario['laps_remaining'],
            gap_ahead=scenario['gap_ahead'],
            gap_behind=scenario['gap_behind']
        )

        print(f"\n   🤖 AI RECOMMENDATION:")
        print(f"      Style: {rec['recommended_style'].value}")
        print(f"      Reason: {rec['reason']}")
        print(f"      Urgency: {rec['urgency']}")

        if rec['alternative_styles']:
            print(f"      Alternatives: {', '.join([s.value for s in rec['alternative_styles']])}")

    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    # Run all demos
    demo_style_impact()
    input("Press ENTER to continue to live style changes demo...")

    demo_live_style_change()
    input("Press ENTER to continue to AI recommendations demo...")

    demo_ai_style_recommendations()

    print("\n" + "="*70)
    print("✅ DRIVING STYLE SYSTEM COMPLETE!")
    print("="*70)
    print("""
ENGINEER CONTROLS:
- Set driving style via dashboard or gesture
- AI recommends style based on race situation
- Style changes tire wear and lap times
- Strategy recalculates in real-time

INTEGRATION POINTS:
1. Frontend: Add driving style selector buttons
2. Coordinator: Call manager.recommend_style() each lap
3. Arduino: Show current style on driver display
4. Gesture: Swipe patterns to change style quickly

NEXT STEPS:
- Integrate into race_monitor_v2.py
- Add to frontend dashboard
- Connect to gesture controls
    """)
    print("="*70 + "\n")
