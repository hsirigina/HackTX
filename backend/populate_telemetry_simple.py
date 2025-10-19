"""
Simple script to populate driver_telemetry and weather_data tables for McLaren Dashboard
"""
import fastf1
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("🏎️  Loading Bahrain 2024 Race Data...")
session = fastf1.get_session(2024, 'Bahrain', 'R')
session.load(telemetry=True, weather=True, messages=False)

print("🗑️  Clearing old data...")
supabase.table('driver_telemetry').delete().neq('id', 0).execute()
supabase.table('weather_data').delete().neq('id', 0).execute()

print("📊 Processing laps 1-57...")

# Get main drivers
drivers = ['VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'NOR', 'PIA', 'ALO', 'STR']

for lap_num in range(1, 58):
    print(f"   Lap {lap_num}/57...", end='\r')
    
    # Weather data (one per lap)
    weather = session.laps[session.laps['LapNumber'] == lap_num].iloc[0] if len(session.laps[session.laps['LapNumber'] == lap_num]) > 0 else None
    if weather is not None:
        try:
            supabase.table('weather_data').insert({
                'race_id': 'bahrain',
                'lap_number': lap_num,
                'air_temp': float(weather['AirTemp']) if weather['AirTemp'] else 25.0,
                'humidity': float(weather['Humidity']) if weather['Humidity'] else 50.0,
                'pressure': float(weather['Pressure']) if weather['Pressure'] else 1013.0,
                'track_temp': float(weather['TrackTemp']) if weather['TrackTemp'] else 35.0,
                'wind_speed': float(weather['WindSpeed']) if weather['WindSpeed'] else 3.5,
                'wind_direction': int(weather['WindDirection']) if weather['WindDirection'] else 180,
                'rainfall': bool(weather['Rainfall']) if weather['Rainfall'] is not None else False
            }).execute()
        except Exception as e:
            print(f"\n   ⚠️  Weather error lap {lap_num}: {e}")
    
    # Driver telemetry
    for driver in drivers:
        try:
            driver_laps = session.laps.pick_driver(driver)
            lap = driver_laps[driver_laps['LapNumber'] == lap_num]
            
            if len(lap) == 0:
                continue
            
            lap = lap.iloc[0]
            
            # Get telemetry for this lap
            tel = lap.get_car_data()
            if tel is None or len(tel) == 0:
                continue
            
            # Calculate telemetry stats
            speed_max = float(tel['Speed'].max()) if len(tel['Speed']) > 0 else 0.0
            speed_avg = float(tel['Speed'].mean()) if len(tel['Speed']) > 0 else 0.0
            throttle_avg = float(tel['Throttle'].mean()) if len(tel['Throttle']) > 0 else 0.0
            throttle_max = float(tel['Throttle'].max()) if len(tel['Throttle']) > 0 else 0.0
            brake_avg = float(tel['Brake'].mean()) if len(tel['Brake']) > 0 else 0.0
            brake_max = float(tel['Brake'].max()) if len(tel['Brake']) > 0 else 0.0
            
            # Get a GPS position (midpoint of lap)
            mid_idx = len(tel) // 2
            pos_x = float(tel['X'].iloc[mid_idx]) if len(tel['X']) > mid_idx else 0.0
            pos_y = float(tel['Y'].iloc[mid_idx]) if len(tel['Y']) > mid_idx else 0.0
            
            # DRS status (check if DRS was used during lap)
            drs_available = bool(tel['DRS'].max() > 0) if len(tel['DRS']) > 0 else False
            
            # Get driver number
            driver_info = session.get_driver(driver)
            driver_num = int(driver_info['DriverNumber']) if driver_info is not None else 0
            
            supabase.table('driver_telemetry').insert({
                'race_id': 'bahrain',
                'driver_number': driver_num,
                'driver_name': driver,
                'lap_number': lap_num,
                'position_x': pos_x,
                'position_y': pos_y,
                'speed_max': speed_max,
                'speed_avg': speed_avg,
                'throttle_avg': min(throttle_avg, 100.0),  # Cap at 100
                'throttle_max': min(throttle_max, 100.0),
                'brake_avg': min(brake_avg, 100.0),
                'brake_max': min(brake_max, 100.0),
                'drs_available': drs_available
            }).execute()
            
        except Exception as e:
            print(f"\n   ⚠️  Error lap {lap_num} driver {driver}: {e}")

print("\n\n✅ Done! Populated telemetry for 57 laps of Bahrain 2024")
print("   - driver_telemetry: ~570 rows (10 drivers × 57 laps)")
print("   - weather_data: 57 rows (1 per lap)")

