"""
Test the fully dynamic AI recommendation system
Shows how AI adapts recommendations based on tire state throughout the race
"""

from interactive_race_simulator import InteractiveRaceSimulator

# Create simulator
sim = InteractiveRaceSimulator(race_year=2024, race_name='Bahrain', total_laps=57, comparison_driver='VER')
sim.start_race(starting_position=3, starting_compound='SOFT')

print("\n" + "="*70)
print("🧪 DYNAMIC AI TEST: RACE FLOW WITH STATE-BASED DECISIONS")
print("="*70)

# Track which laps offer decisions
decision_laps_offered = []

for lap in range(1, 58):
    # Simulate the lap
    if sim.state.current_lap == lap:
        lap_time, _ = sim.simulate_lap(lap)
        sim.state.current_lap += 1
    
    # Check if decision should be offered
    should_offer = sim.should_offer_decision(lap)
    
    if should_offer:
        decision_laps_offered.append(lap)
        
        # Get tire state
        max_laps = sim.tire_model.COMPOUND_WEAR_RATES[sim.state.tire_compound]['max_laps']
        tire_pct = (sim.state.tire_age / max_laps) * 100
        
        # Generate options
        options = sim.generate_decision_options(lap)
        
        # Find recommended option
        recommended = next((opt for opt in options if opt.ai_confidence in ['HIGHLY_RECOMMENDED', 'RECOMMENDED']), None)
        
        print(f"\nLap {lap:2d} | Tire: {sim.state.tire_compound} {sim.state.tire_age}/{max_laps} ({tire_pct:.0f}%) | Pits: {len(sim.state.pit_stops)}")
        print(f"        | DECISION TRIGGER: {'CRITICAL - PAST CLIFF!' if tire_pct >= 100 else 'Approaching cliff' if tire_pct >= 70 else 'Mid-stint' if tire_pct >= 40 else 'Tactical'}")
        
        if recommended:
            emoji = '⭐' if recommended.ai_confidence == 'HIGHLY_RECOMMENDED' else '✅'
            print(f"        | {emoji} {recommended.ai_confidence}: {recommended.title}")
            print(f"        |    Impact: {recommended.predicted_race_time_impact:+.1f}s")
        else:
            print(f"        | ⚠️  NO RECOMMENDED OPTION (all alternatives!)")
        
        # Auto-select recommended option for simulation
        if recommended:
            result = sim.execute_decision(recommended)

print(f"\n" + "="*70)
print(f"✅ RACE COMPLETE")
print(f"="*70)
print(f"Decision laps offered: {len(decision_laps_offered)}")
print(f"Laps: {decision_laps_offered[:10]}... (first 10)")
print(f"Final time: {sim.state.total_race_time:.1f}s")
print(f"VER's time: {sim.comparison_total_time:.1f}s")
print(f"Gap: {sim.state.total_race_time - sim.comparison_total_time:+.1f}s")
print(f"Pit stops: {len(sim.state.pit_stops)}")
for i, pit in enumerate(sim.state.pit_stops, 1):
    print(f"  Pit {i}: Lap {pit['lap']} → {pit['compound']}")
