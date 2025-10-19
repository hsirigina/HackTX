import fastf1
import warnings
warnings.filterwarnings('ignore')

# Load the race data
session = fastf1.get_session(2024, 'Bahrain', 'R')
session.load()

# Get lap 57 cumulative times for all drivers
print("LAP 57 CUMULATIVE TIMES (All Drivers):")
print("-" * 50)

# Check all drivers and their lap counts
print("\nDRIVER LAP COUNTS:")
for driver_num in session.laps['DriverNumber'].unique():
    driver_laps = session.laps[session.laps['DriverNumber'] == driver_num]
    max_lap = driver_laps['LapNumber'].max()
    driver_abbr = driver_laps.iloc[0]['Driver']
    print(f"{driver_abbr} (#{driver_num}): {max_lap} laps")

print("\n" + "=" * 50)

standings = []
for driver_num in session.laps['DriverNumber'].unique():
    driver_laps = session.laps[session.laps['DriverNumber'] == driver_num]
    laps_completed = driver_laps[driver_laps['LapNumber'] <= 57]

    if len(laps_completed) >= 57:  # Only include drivers who completed all 57 laps
        cumulative_time = laps_completed['LapTime'].sum().total_seconds()
        driver_abbr = driver_laps.iloc[0]['Driver']
        standings.append({
            'driver': driver_abbr,
            'number': driver_num,
            'time': cumulative_time
        })

# Sort by time
standings.sort(key=lambda x: x['time'])

# Print all positions
for i, entry in enumerate(standings, 1):
    print(f"P{i:2}: {entry['driver']} (#{entry['number']}) - {entry['time']:.1f}s")

print("\n" + "=" * 50)
print("YOUR SIMULATED TIME: 5592.3s")
print("This would place you in P20")
print("=" * 50)

# Show the gap analysis
your_time = 5592.3
print("\nGAPS TO NEARBY POSITIONS:")
for i, entry in enumerate(standings, 1):
    if 10 <= i <= 20:
        gap = your_time - entry['time']
        marker = ""
        if i < len(standings) and i > 0:
            if standings[i-1]['time'] < your_time and entry['time'] > your_time:
                marker = " <-- YOU would be here"
        print(f"P{i:2}: {entry['driver']} - Gap: {gap:+.1f}s{marker}")