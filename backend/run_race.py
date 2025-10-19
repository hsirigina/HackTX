"""
FINAL CLEAN RACE SIMULATOR
6 decisions total:
- 4 tactical (lap 1, 10, 30, 55)
- 2 pit windows (when tire hits 70% wear)

Fixes:
- No double tire age increment
- Pit window only shown once per stint
- Tire age resets properly on pit
"""

from interactive_race_simulator import InteractiveRaceSimulator
from pit_window_selector import PitWindowSelector
from driving_style import DrivingStyle, DrivingStyleManager


def show_options(options, lap, title):
    """Display 3 tactical options"""
    print("\n" + "="*70)
    print(f"📍 LAP {lap} - {title}")
    print("="*70)
    for i, opt in enumerate(options, 1):
        emoji = {'HIGHLY_RECOMMENDED': '⭐', 'RECOMMENDED': '✅', 'ALTERNATIVE': '🔧'}[opt['conf']]
        print(f"\n{emoji} OPTION {i}: {opt['name']}")
        print(f"   {opt['desc']}")
        print(f"   Impact: {opt['impact']}")
    print("\n" + "="*70)


def get_choice():
    while True:
        try:
            c = int(input("\n👉 Enter choice (1-3): "))
            if 1 <= c <= 3:
                return c - 1
            print("❌ Enter 1, 2, or 3")
        except (ValueError, KeyboardInterrupt):
            if KeyboardInterrupt:
                print("\n\n🏁 Abandoned!")
                exit()
            print("❌ Enter a number")


def show_pit_window(window, current_lap):
    """Show pit window timeline - ONLY FUTURE LAPS"""
    print("\n" + "="*70)
    print(f"📍 LAP {current_lap} - PIT DECISION")
    print("="*70)
    print(f"\n📊 Tire: {window['current_state']['compound']}, {window['current_state']['tire_age']} laps old")
    print(f"   Cliff at lap {window['current_state']['cliff_lap']} ({window['current_state']['laps_to_cliff']} laps away)")
    print(f"\n🎯 AI RECOMMENDS: Pit lap {window['optimal_lap']} for {window['optimal_compound']}")

    # Timeline - ONLY show future laps (after current lap)
    timeline = ""
    shown_count = 0
    for lap_info in window['lap_details']:
        if lap_info.lap_number > current_lap and shown_count < 12:
            emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}[lap_info.color]
            timeline += f"{emoji}{lap_info.lap_number} "
            shown_count += 1

    print(f"\n📅 FUTURE PIT WINDOW:")
    print(f"   {timeline}")
    print("   🟢=OPTIMAL  🟡=ACCEPTABLE  🔴=RISKY")
    print("\n" + "="*70)


def get_pit_lap(current, max_lap, optimal):
    while True:
        try:
            choice = input(f"👉 Pit on lap (rec: {optimal}): ").strip()
            lap = int(choice)
            if lap <= current:
                print(f"❌ Must be after lap {current}")
            elif lap > max_lap:
                print(f"❌ Race ends at lap {max_lap}")
            else:
                return lap
        except (ValueError, KeyboardInterrupt):
            if KeyboardInterrupt:
                print("\n\n🏁 Abandoned!")
                exit()
            print("❌ Enter a number")


print("="*70)
print("🏎️  F1 RACE SIMULATOR - BAHRAIN 2024")
print("="*70)
print("\n📋 Beat Verstappen's time!")
print("📋 6 decisions: 4 tactical + 2 pit stops\n")
input("Press ENTER to start... ")

# Setup
sim = InteractiveRaceSimulator(2024, 'Bahrain', 57, 'VER', demo_mode=False)
info = sim.start_race(starting_position=3, starting_compound='SOFT')
print(f"\n🎯 TARGET: {info['comparison_time']:.1f}s\n")

selector = PitWindowSelector(sim.tire_model, 57)

# === DECISION 1: DRIVING STYLE ===
opts = [
    {'name': 'AGGRESSIVE', 'desc': 'Fast laps, high wear', 'impact': '-0.3s/lap, +40% wear', 'conf': 'RECOMMENDED', 'style': DrivingStyle.AGGRESSIVE},
    {'name': 'BALANCED', 'desc': 'Standard pace', 'impact': 'Normal', 'conf': 'HIGHLY_RECOMMENDED', 'style': DrivingStyle.BALANCED},
    {'name': 'CONSERVATIVE', 'desc': 'Save tires', 'impact': '+0.4s/lap, -30% wear', 'conf': 'ALTERNATIVE', 'style': DrivingStyle.CONSERVATIVE}
]
show_options(opts, 1, "DRIVING STYLE")
choice = get_choice()
sim.state.driving_style = opts[choice]['style']
print(f"\n✅ {opts[choice]['name']}")

# Update tire model
sim.tire_model.driving_style_multiplier = DrivingStyleManager(sim.state.driving_style).get_tire_wear_multiplier()

# Track state
pit_plan = None  # Tuple: (lap, compound)
first_pit_done = False
second_pit_done = False

# === SIMULATE RACE ===
for lap in range(1, 58):
    # Execute planned pit
    if pit_plan and pit_plan[0] == lap:
        print(f"\n⏩ LAP {lap} - PITTING FOR {pit_plan[1]}")
        sim.state.tire_compound = pit_plan[1]
        sim.state.tire_age = 0  # RESET!
        sim.state.total_race_time += 25.0
        sim.state.pit_stops.append({'lap': lap, 'compound': pit_plan[1], 'reason': 'Planned'})
        print(f"✅ Pitted (+25s)")

        if not first_pit_done:
            first_pit_done = True
        else:
            second_pit_done = True
        pit_plan = None

    # Simulate lap (this increments tire_age internally!)
    lap_time, _ = sim.simulate_lap(lap)
    sim.state.current_lap = lap + 1

    # Check tire wear
    max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
    tire_pct = sim.state.tire_age / max_laps

    # === DECISION 2: LAP 10 TACTICAL ===
    if lap == 10:
        opts = [
            {'name': 'PUSH', 'desc': 'Attack ahead', 'impact': '-0.2s/lap, +20% wear', 'conf': 'RECOMMENDED'},
            {'name': 'MAINTAIN', 'desc': 'Hold pace', 'impact': 'No change', 'conf': 'HIGHLY_RECOMMENDED'},
            {'name': 'CONSERVE', 'desc': 'Save tires', 'impact': '+0.2s/lap, -20% wear', 'conf': 'ALTERNATIVE'}
        ]
        show_options(opts, 10, "TACTICAL")
        choice = get_choice()
        print(f"\n✅ {opts[choice]['name']}")

    # === DECISION 3: FIRST PIT WINDOW (50% tire - EARLY to plan ahead!) ===
    # Trigger at 50% so user can see future optimal window (not current lap)
    if tire_pct >= 0.50 and tire_pct < 0.55 and not first_pit_done and pit_plan is None:
        window = selector.generate_pit_window(lap, sim.state.tire_age, sim.state.tire_compound, 57 - lap)
        show_pit_window(window, lap)
        pit_lap = get_pit_lap(lap, 57, window['optimal_lap'])
        pit_plan = (pit_lap, window['optimal_compound'])
        print(f"\n✅ Planned: Pit lap {pit_lap} for {window['optimal_compound']}")

    # === DECISION 4: LAP 30 TACTICAL ===
    if lap == 30:
        opts = [
            {'name': 'ATTACK', 'desc': 'Close gap', 'impact': '-0.3s/lap, +30% wear', 'conf': 'RECOMMENDED'},
            {'name': 'HOLD', 'desc': 'Maintain', 'impact': 'No change', 'conf': 'HIGHLY_RECOMMENDED'},
            {'name': 'MANAGE', 'desc': 'Extend stint', 'impact': '+0.3s/lap, -30% wear', 'conf': 'ALTERNATIVE'}
        ]
        show_options(opts, 30, "MID-RACE")
        choice = get_choice()
        print(f"\n✅ {opts[choice]['name']}")

    # === DECISION 5: SECOND PIT WINDOW (50% tire on stint 2 - EARLY!) ===
    # Trigger at 50% again so user can plan ahead for second pit
    if tire_pct >= 0.50 and tire_pct < 0.55 and first_pit_done and not second_pit_done and pit_plan is None and (57 - lap) > 10:
        window = selector.generate_pit_window(lap, sim.state.tire_age, sim.state.tire_compound, 57 - lap)
        show_pit_window(window, lap)
        pit_lap = get_pit_lap(lap, 57, window['optimal_lap'])
        pit_plan = (pit_lap, window['optimal_compound'])
        print(f"\n✅ Planned: Pit lap {pit_lap} for {window['optimal_compound']}")

    # === DECISION 6: LAP 55 FINAL ===
    if lap == 55:
        opts = [
            {'name': 'QUALI MODE', 'desc': 'All-out', 'impact': '-0.8s/lap, 200% wear', 'conf': 'HIGHLY_RECOMMENDED'},
            {'name': 'PUSH', 'desc': 'Strong pace', 'impact': '-0.3s/lap, 120% wear', 'conf': 'RECOMMENDED'},
            {'name': 'BRING HOME', 'desc': 'Safe', 'impact': '+0.2s/lap, 80% wear', 'conf': 'ALTERNATIVE'}
        ]
        show_options(opts, 55, "FINAL LAPS")
        choice = get_choice()
        print(f"\n✅ {opts[choice]['name']}")

    # Progress
    if lap % 10 == 0 and lap not in [10, 30]:
        print(f"⏩ Lap {lap}/57 | {sim.state.tire_compound} {sim.state.tire_age} laps | {len(sim.state.pit_stops)} pits")

# === RESULTS ===
final = sim.get_final_comparison()

print("\n" + "="*70)
print("🏁 FINISHED!")
print("="*70)
print(f"\n🏆 PERFORMANCE:")
print(f"   Your time:  {final['user_time']:.1f}s")
print(f"   Winner:     {final['full_leaderboard'][0]['time']:.1f}s ({final['full_leaderboard'][0]['driver']})")
print(f"   Gap:        +{final['gap_to_winner']:.1f}s")
print(f"   Position:   P{final['leaderboard_position']}/{final['total_drivers']}")

print(f"\n📊 LEADERBOARD:")
print("="*70)
for d in final['nearby_drivers']:
    marker = '👉' if d['driver'] == 'YOU' else '  '
    print(f"{marker} {d['driver']:3s}  {d['team']:25s}  {d['time']:.1f}s")

print(f"\n📋 STRATEGY:")
print(f"   Style: {sim.state.driving_style.value}")
print(f"   Pits: {len(sim.state.pit_stops)}")
for i, p in enumerate(sim.state.pit_stops, 1):
    print(f"   #{i}: Lap {p['lap']} → {p['compound']}")

print("\n" + "="*70)
print("Thanks for racing! 🏎️")
print("="*70)
