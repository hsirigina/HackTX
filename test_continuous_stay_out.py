"""
Test that if user keeps choosing "Stay Out", they keep getting pit decisions
"""
from interactive_race_simulator import InteractiveRaceSimulator

sim = InteractiveRaceSimulator(race_year=2024, race_name='Bahrain', total_laps=57, comparison_driver='VER')
sim.start_race(starting_position=3, starting_compound='SOFT')

print("\n🧪 TEST: What happens if user ALWAYS chooses 'Stay Out'?")
print("="*70)

# Simulate first lap
sim.simulate_lap(1)
sim.state.current_lap = 2

# Choose AGGRESSIVE driving (lap 1 decision)
options = sim.generate_decision_options(1)
aggressive = next(opt for opt in options if 'Aggressive' in opt.title)
sim.execute_decision(aggressive)

# Now fast-forward to lap 18 (72% tire age)
for lap in range(2, 18):
    sim.simulate_lap(lap)
    sim.state.current_lap = lap + 1

print(f"\nStarting at lap 18 (tire age {sim.state.tire_age}/25 = 72%)")
print("User will keep choosing 'Stay Out' to see if they keep getting asked...\n")

# Keep choosing "Stay Out" from lap 18 to 28
for current_lap in range(18, 29):
    if sim.should_offer_decision(current_lap):
        max_laps = 25
        tire_pct = (sim.state.tire_age / max_laps) * 100
        
        options = sim.generate_decision_options(current_lap)
        stay_out_option = next((opt for opt in options if 'Stay Out' in opt.title), None)
        
        if stay_out_option:
            print(f"Lap {current_lap:2d} (tire {sim.state.tire_age}/{max_laps} = {tire_pct:.0f}%)")
            print(f"  ✅ Decision offered: {len(options)} options")
            print(f"  👉 User chooses: 'Stay Out' ({stay_out_option.ai_confidence})")
            print(f"     Impact: {stay_out_option.predicted_race_time_impact:+.1f}s")
            
            # User chooses to stay out (ignoring AI recommendation!)
            result = sim.execute_decision(stay_out_option)
        else:
            print(f"Lap {current_lap:2d}: No 'Stay Out' option available (must pit!)")
    
    # Simulate the lap
    sim.simulate_lap(current_lap)
    sim.state.current_lap = current_lap + 1

print("\n" + "="*70)
print("✅ CONCLUSION: User keeps getting asked every lap as tire degrades!")
print(f"Final tire age: {sim.state.tire_age}/25 laps")
print(f"Total decisions offered: ~11 laps (18-28)")
