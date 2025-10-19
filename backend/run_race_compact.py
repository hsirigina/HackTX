"""
F1 Race Simulator - COMPACT OUTPUT FOR DEBUGGING
Only shows decisions and final summary (copy-paste friendly)
"""

from interactive_race_simulator import InteractiveRaceSimulator
from pit_window_selector import PitWindowSelector
from driving_style import DrivingStyle, DrivingStyleManager

# Track all decisions for summary
decision_log = []

def calculate_live_position(sim, current_lap):
    """
    Calculate current race position by comparing cumulative times
    Returns: (position, gap_to_ahead, gap_to_behind, leader_gap)
    """
    if current_lap < 1:
        return 3, 0.0, 0.0, 0.0

    # Get all drivers' cumulative times at this lap
    standings = []
    for driver in sim.race_data['DriverNumber'].unique():
        driver_laps = sim.race_data[sim.race_data['DriverNumber'] == driver]
        laps_completed = driver_laps[driver_laps['LapNumber'] <= current_lap]

        if len(laps_completed) > 0:
            cumulative_time = laps_completed['LapTime'].sum().total_seconds()
            standings.append({
                'driver': driver,
                'time': cumulative_time
            })

    # Add user's time
    standings.append({
        'driver': 'YOU',
        'time': sim.state.total_race_time
    })

    # Sort by time
    standings.sort(key=lambda x: x['time'])

    # Find user position
    user_idx = next(i for i, s in enumerate(standings) if s['driver'] == 'YOU')
    position = user_idx + 1

    # Calculate gaps
    gap_to_ahead = 0.0 if user_idx == 0 else sim.state.total_race_time - standings[user_idx - 1]['time']
    gap_to_behind = 0.0 if user_idx == len(standings) - 1 else standings[user_idx + 1]['time'] - sim.state.total_race_time
    leader_gap = sim.state.total_race_time - standings[0]['time'] if user_idx > 0 else 0.0

    return position, gap_to_ahead, gap_to_behind, leader_gap

def log_decision(lap, category, recommended, chosen, extra=""):
    """Log a decision for final summary"""
    decision_log.append({
        'lap': lap,
        'category': category,
        'recommended': recommended,
        'chosen': chosen,
        'extra': extra
    })

def show_options(opts, lap, title):
    print(f"\n📍 LAP {lap} - {title}")
    for i, opt in enumerate(opts, 1):
        emoji = {'HIGHLY_RECOMMENDED': '⭐', 'RECOMMENDED': '✅', 'ALTERNATIVE': '🔧'}[opt['conf']]
        print(f"{emoji} {i}. {opt['name']}: {opt['impact']}")

def get_choice():
    while True:
        try:
            c = int(input("Choice (1-3): "))
            if 1 <= c <= 3:
                return c - 1
        except (ValueError, KeyboardInterrupt):
            if KeyboardInterrupt:
                exit()
        print("Enter 1, 2, or 3")

def show_pit_window(window, lap):
    print(f"\n📍 LAP {lap} - PIT WINDOW")
    print(f"Tire: {window['current_state']['compound']} {window['current_state']['tire_age']} laps ({window['current_state']['tire_age']/25*100:.0f}%)")
    print(f"Cliff: Lap {window['current_state']['cliff_lap']}")
    print(f"⭐ RECOMMEND: Lap {window['optimal_lap']} for {window['optimal_compound']}")

    # Timeline
    timeline = ""
    for lap_info in window['lap_details']:
        if lap_info.lap_number > lap and len(timeline) < 150:
            emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}[lap_info.color]
            timeline += f"{emoji}{lap_info.lap_number} "
    print(f"Future: {timeline}")
    print("🟢=Optimal(70-85%) 🟡=Early 🔴=Risky")

def get_pit_lap(current, max_lap, optimal):
    while True:
        try:
            lap = int(input(f"Pit lap (rec {optimal}): "))
            if current < lap <= max_lap:
                return lap
            print(f"Must be {current+1}-{max_lap}")
        except (ValueError, KeyboardInterrupt):
            if KeyboardInterrupt:
                exit()
            print("Enter number")

def show_tire_options(laps_remaining, optimal_compound, tire_model, current_wear_multiplier):
    """Show tire compound options with context - dynamically calculated from tire model"""
    print(f"\n🔧 TIRE COMPOUND CHOICE")
    print(f"Laps remaining: {laps_remaining}")
    print(f"⭐ RECOMMEND: {optimal_compound}")

    # Get max laps from tire model (adjusted for current wear multiplier)
    soft_max = int(tire_model.COMPOUND_WEAR_RATES['SOFT']['max_laps'] / current_wear_multiplier)
    medium_max = int(tire_model.COMPOUND_WEAR_RATES['MEDIUM']['max_laps'] / current_wear_multiplier)
    hard_max = int(tire_model.COMPOUND_WEAR_RATES['HARD']['max_laps'] / current_wear_multiplier)

    print(f"\n📊 Tire capabilities (adjusted for your driving style {current_wear_multiplier:.1f}x):")
    print(f"   🔴 SOFT:   ~{soft_max} laps max (fastest, wears quickly)")
    print(f"   🟡 MEDIUM: ~{medium_max} laps max (balanced)")
    print(f"   ⚪ HARD:   ~{hard_max} laps max (slowest, very durable)")

    opts = []
    # SOFT - viable if laps remaining within 90% of max (safety margin)
    if laps_remaining <= soft_max * 0.9:
        opts.append({'name': 'SOFT', 'conf': 'HIGHLY_RECOMMENDED' if optimal_compound == 'SOFT' else 'RECOMMENDED'})
    elif laps_remaining <= soft_max * 1.1:
        opts.append({'name': 'SOFT', 'conf': 'RISKY'})
    else:
        opts.append({'name': 'SOFT', 'conf': 'RISKY'})

    # MEDIUM - viable if laps remaining within 90% of max
    if laps_remaining <= medium_max * 0.9:
        opts.append({'name': 'MEDIUM', 'conf': 'HIGHLY_RECOMMENDED' if optimal_compound == 'MEDIUM' else 'RECOMMENDED'})
    elif laps_remaining <= medium_max * 1.1:
        opts.append({'name': 'MEDIUM', 'conf': 'RISKY'})
    else:
        opts.append({'name': 'MEDIUM', 'conf': 'RISKY'})

    # HARD - always available
    if laps_remaining <= hard_max * 0.9:
        opts.append({'name': 'HARD', 'conf': 'HIGHLY_RECOMMENDED' if optimal_compound == 'HARD' else 'ALTERNATIVE'})
    else:
        opts.append({'name': 'HARD', 'conf': 'RECOMMENDED'})

    print()
    for i, opt in enumerate(opts, 1):
        emoji = {'HIGHLY_RECOMMENDED': '⭐', 'RECOMMENDED': '✅', 'ALTERNATIVE': '🔧', 'RISKY': '⚠️'}[opt['conf']]
        print(f"{emoji} {i}. {opt['name']}")

    return opts

def get_tire_choice(opts):
    while True:
        try:
            c = int(input(f"Tire choice (1-{len(opts)}): "))
            if 1 <= c <= len(opts):
                return c - 1
        except (ValueError, KeyboardInterrupt):
            if KeyboardInterrupt:
                exit()
        print(f"Enter 1-{len(opts)}")

# Setup - DYNAMIC RACE CONFIGURATION
RACE_YEAR = 2024
RACE_NAME = 'Bahrain'  # Change to: 'Monaco', 'Silverstone', 'Monza', etc.
COMPARISON_DRIVER = 'VER'  # Change to any driver code
STARTING_POSITION = 3
STARTING_COMPOUND = 'SOFT'

print(f"🏎️  F1 {RACE_NAME.upper()} {RACE_YEAR} - COMPACT MODE")
input("Press ENTER... ")

# Initialize simulator - it will fetch total_laps from FastF1 data
sim = InteractiveRaceSimulator(RACE_YEAR, RACE_NAME, None, COMPARISON_DRIVER, demo_mode=False)
info = sim.start_race(starting_position=STARTING_POSITION, starting_compound=STARTING_COMPOUND)

# Get total laps dynamically from loaded race data
TOTAL_LAPS = sim.total_laps
print(f"   Race length: {TOTAL_LAPS} laps")

selector = PitWindowSelector(sim.tire_model, TOTAL_LAPS)

# State
pit_plan = None
first_pit_done = False
second_pit_done = False
pace_modifier = 0.0  # Cumulative lap time adjustment from tactical decisions
wear_multiplier = 1.0  # Cumulative tire wear multiplier from tactical decisions
effective_tire_age = 0.0  # Track fractional tire wear (aggressive = ages faster)

# Rule-based decision tracking with rate limiting
last_tactical_lap = 0  # Track when last tactical decision was made
last_pit_decision_lap = 0  # Track when last pit decision was made
pit_count = 0  # Track number of pits completed

# Rate limits (in laps)
TACTICAL_COOLDOWN = 10  # One tactical decision every 10 laps
PIT_DECISION_COOLDOWN = 5  # Can't show pit window again for 5 laps

# === DECISION 1: STYLE ===
opts = [
    {'name': 'AGGRESSIVE', 'impact': '-0.3s/lap +40%wear', 'conf': 'RECOMMENDED', 'style': DrivingStyle.AGGRESSIVE, 'pace': -0.3, 'wear': 1.4},
    {'name': 'BALANCED', 'impact': 'Normal', 'conf': 'HIGHLY_RECOMMENDED', 'style': DrivingStyle.BALANCED, 'pace': 0.0, 'wear': 1.0},
    {'name': 'CONSERVATIVE', 'impact': '+0.4s/lap -30%wear', 'conf': 'ALTERNATIVE', 'style': DrivingStyle.CONSERVATIVE, 'pace': 0.4, 'wear': 0.7}
]
show_options(opts, 1, "STYLE")
c = get_choice()
sim.state.driving_style = opts[c]['style']
pace_modifier = opts[c]['pace']
wear_multiplier = opts[c]['wear']
sim.tire_model.driving_style_multiplier = wear_multiplier  # SET IMMEDIATELY
log_decision(1, 'STYLE', 'BALANCED', opts[c]['name'])
print(f"✅ {opts[c]['name']} (Pace: {pace_modifier:+.1f}s/lap, Wear: {wear_multiplier:.1f}x)")

# === SIMULATE ===
for lap in range(1, TOTAL_LAPS + 1):
    # Pit if planned
    if pit_plan and pit_plan[0] == lap:
        print(f"\n⏩ LAP {lap} - PITTING {pit_plan[1]}")
        sim.state.tire_compound = pit_plan[1]
        sim.state.tire_age = 0
        effective_tire_age = 0.0  # RESET effective age too
        sim.state.total_race_time += 25.0
        sim.state.pit_stops.append({'lap': lap, 'compound': pit_plan[1], 'reason': 'Planned'})
        pit_count += 1
        if not first_pit_done:
            first_pit_done = True
        else:
            second_pit_done = True
        pit_plan = None

    # Apply tactical wear multiplier BEFORE simulating lap
    # This affects the tire degradation calculation
    sim.tire_model.driving_style_multiplier = wear_multiplier

    # Simulate
    sim.simulate_lap(lap)
    sim.state.current_lap = lap + 1

    # Increment effective tire age based on wear multiplier
    # Aggressive driving = tires age faster (e.g. 1.4 laps per lap)
    # Conservative = tires age slower (e.g. 0.7 laps per lap)
    effective_tire_age += wear_multiplier

    # Override tire_age with effective age for pit window calculations
    # Use int() to keep it as valid index, but it advances faster/slower
    sim.state.tire_age = int(effective_tire_age)

    # Apply tactical pace modifier
    sim.state.total_race_time += pace_modifier

    max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
    tire_pct = sim.state.tire_age / max_laps

    # Calculate live position and gaps
    position, gap_ahead, gap_behind, leader_gap = calculate_live_position(sim, lap)
    sim.state.position = position  # Update state

    # Show progress only at key moments (not every lap)
    # This creates a "fast-forward" feeling between decisions

    # === TACTICAL DECISION (Rule-based with rate limiting) ===
    # Triggers when opportunity exists AND cooldown has passed
    tactical_opportunity = (
        abs(gap_ahead) < 3.0 or  # Close to car ahead - can attack
        gap_behind < 2.0 or      # Car behind is close - need to defend
        (position <= 3 and abs(leader_gap) < 10.0)  # Fighting for podium
    )

    if tactical_opportunity and (lap - last_tactical_lap) >= TACTICAL_COOLDOWN:
        print()  # Clear fast-forward line

        # Determine context for recommendation
        if abs(gap_ahead) < 3.0:
            context = f"Close gap: {abs(gap_ahead):.1f}s ahead"
            recommended = 0  # PUSH
        elif gap_behind < 2.0:
            context = f"Under pressure: {gap_behind:.1f}s behind"
            recommended = 0  # PUSH
        else:
            context = f"P{position} - Managing position"
            recommended = 1  # MAINTAIN

        opts = [
            {'name': 'PUSH', 'impact': '-0.2s/lap +20%wear', 'conf': 'RECOMMENDED' if recommended == 0 else 'ALTERNATIVE', 'pace': -0.2, 'wear': 0.2},
            {'name': 'MAINTAIN', 'impact': 'No change', 'conf': 'HIGHLY_RECOMMENDED' if recommended == 1 else 'ALTERNATIVE', 'pace': 0.0, 'wear': 0.0},
            {'name': 'CONSERVE', 'impact': '+0.2s/lap -20%wear', 'conf': 'RECOMMENDED' if recommended == 2 else 'ALTERNATIVE', 'pace': 0.2, 'wear': -0.2}
        ]

        print(f"🎯 {context}")
        show_options(opts, lap, "TACTICAL")
        c = get_choice()
        pace_modifier += opts[c]['pace']
        wear_multiplier += opts[c]['wear']
        log_decision(lap, 'TACTICAL', opts[recommended]['name'], opts[c]['name'], context)
        print(f"✅ {opts[c]['name']} (Total Pace: {pace_modifier:+.1f}s/lap, Wear: {wear_multiplier:.1f}x)")
        last_tactical_lap = lap

    # === PIT DECISION (Rule-based with rate limiting) ===
    # Triggers when tire wear crosses threshold AND cooldown has passed
    pit_opportunity = (
        tire_pct >= 0.50 and  # Tires at 50%+ wear
        pit_plan is None and  # No pit already planned
        (TOTAL_LAPS - lap) > 10 and   # Enough laps remaining to make pit worthwhile
        (lap - last_pit_decision_lap) >= PIT_DECISION_COOLDOWN  # Cooldown passed
    )

    if pit_opportunity:
        print()  # Clear fast-forward line
        window = selector.generate_pit_window(lap, sim.state.tire_age, sim.state.tire_compound, TOTAL_LAPS - lap)
        show_pit_window(window, lap)

        # Get green zone for logging
        green_laps = window['recommended_window']
        green_zone = f"{green_laps[0]}-{green_laps[-1]}" if green_laps else "none"

        # Step 1: Choose pit lap
        pit_lap = get_pit_lap(lap, TOTAL_LAPS, window['optimal_lap'])

        # Step 2: Choose tire compound
        laps_remaining_after_pit = TOTAL_LAPS - pit_lap
        tire_opts = show_tire_options(laps_remaining_after_pit, window['optimal_compound'], sim.tire_model, wear_multiplier)
        tire_choice = get_tire_choice(tire_opts)
        chosen_compound = tire_opts[tire_choice]['name']

        pit_plan = (pit_lap, chosen_compound)

        log_decision(lap, f'PIT{pit_count + 1}',
                    f"Lap {window['optimal_lap']} {window['optimal_compound']}",
                    f"Lap {pit_lap} {chosen_compound}",
                    f"Green:{green_zone}")
        print(f"✅ Planned: Lap {pit_lap} → {chosen_compound} tires")
        last_pit_decision_lap = lap

    # Fast-forward progress indicator (show every 5 laps)
    if lap % 5 == 0:
        gap_display = f"+{gap_ahead:.1f}s" if gap_ahead > 0 else f"{gap_ahead:.1f}s"
        print(f"⏩ Lap {lap}/{TOTAL_LAPS} | P{position} | Gap ahead: {gap_display} | {sim.state.tire_compound} {tire_pct:.0%} worn", end='\r', flush=True)

# === COMPACT SUMMARY ===
print()  # Clear the fast-forward line
print("\n🏁 Race Complete! Analyzing results...\n")
final = sim.get_final_comparison()

print("\n" + "="*80)
print("📋 RACE SUMMARY - COPY THIS SECTION FOR DEBUGGING")
print("="*80)

print(f"\n🏁 RESULT: {final['user_time']:.1f}s | Gap: +{final['gap_to_winner']:.1f}s | P{final['leaderboard_position']}/{final['total_drivers']}")
print(f"   Winner: {final['full_leaderboard'][0]['driver']} {final['full_leaderboard'][0]['time']:.1f}s")

print(f"\n📊 DECISIONS:")
for d in decision_log:
    if d['category'] in ['PIT1', 'PIT2']:
        print(f"   Lap {d['lap']:2d} {d['category']:8s} | Rec: {d['recommended']:20s} | Chose: {d['chosen']:20s} | {d['extra']}")
    else:
        print(f"   Lap {d['lap']:2d} {d['category']:8s} | Rec: {d['recommended']:15s} | Chose: {d['chosen']:15s}")

print(f"\n🔧 PIT STOPS:")
for i, p in enumerate(sim.state.pit_stops, 1):
    print(f"   #{i}: Lap {p['lap']} → {p['compound']}")

print(f"\n🔍 FINAL STATE:")
print(f"   Final tire: {sim.state.tire_compound} {sim.state.tire_age} laps old")
print(f"   Total pits: {len(sim.state.pit_stops)}")
print(f"   Final pace modifier: {pace_modifier:+.1f}s/lap (applied to all {TOTAL_LAPS} laps = {pace_modifier * TOTAL_LAPS:+.1f}s)")
print(f"   Final wear multiplier: {wear_multiplier:.2f}x")

print("\n" + "="*80)
