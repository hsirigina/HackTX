"""
Test to verify tire cliff is being applied in simulator
"""

from interactive_race_simulator import InteractiveRaceSimulator

# Create simulator
sim = InteractiveRaceSimulator(
    race_year=2024,
    race_name='Bahrain',
    total_laps=57,
    comparison_driver='VER'
)

# Start race
sim.start_race(starting_position=3, starting_compound='SOFT')

print("\n" + "="*70)
print("SIMULATING RACE WITHOUT PITTING (Testing tire cliff)")
print("="*70)

# Simulate all laps without pitting
for lap in range(1, 58):
    sim.state.current_lap = lap
    lap_time, lap_info = sim.simulate_lap(lap)

    # Show key laps
    if lap in [1, 10, 20, 25, 26, 27, 30, 35, 40, 45, 50, 55, 57]:
        print(f"Lap {lap:2d}: {lap_time:8.2f}s (tire age: {lap_info['tire_age']:2d}, total: {lap_info['cumulative_time']:.1f}s)")

print("\n" + "="*70)
print(f"FINAL RACE TIME: {sim.state.total_race_time:.1f}s")
print(f"VER'S ACTUAL TIME: {sim.comparison_total_time:.1f}s")
print(f"DIFFERENCE: {sim.state.total_race_time - sim.comparison_total_time:+.1f}s")
print("="*70)

if sim.state.total_race_time < sim.comparison_total_time:
    print("❌ UNREALISTIC: You beat VER without pitting!")
else:
    print("✅ REALISTIC: Running 57 laps on SOFT is slower than VER's 2-stop strategy")
