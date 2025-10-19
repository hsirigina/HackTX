"""
Test if race comparison visualization is ready
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def test_visualization_setup():
    """Check if race_comparison table exists and is accessible"""

    print("\n🔍 Checking Race Comparison Visualization Setup...")
    print("="*60)

    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    # Try to query race_comparison table
    try:
        response = supabase.table('race_comparison').select('*').limit(1).execute()
        print("✅ race_comparison table exists and is accessible")
        print(f"   Found {len(response.data)} record(s)")
        return True

    except Exception as e:
        error_msg = str(e)

        if 'relation "public.race_comparison" does not exist' in error_msg or 'does not exist' in error_msg:
            print("❌ race_comparison table does NOT exist")
            print("\n📋 TO FIX: Run this SQL in Supabase SQL Editor:")
            print("="*60)
            print("""
CREATE TABLE race_comparison (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  driver_name TEXT NOT NULL,
  lap_number INTEGER NOT NULL,

  ai_cumulative_time FLOAT NOT NULL,
  ai_tire_compound TEXT NOT NULL,
  ai_tire_age INTEGER NOT NULL,
  ai_has_pitted BOOLEAN DEFAULT FALSE,
  ai_pit_lap INTEGER,

  baseline_cumulative_time FLOAT NOT NULL,
  baseline_tire_compound TEXT NOT NULL,
  baseline_tire_age INTEGER NOT NULL,
  baseline_has_pitted BOOLEAN DEFAULT FALSE,
  baseline_pit_lap INTEGER,

  time_difference FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(race_id, driver_name, lap_number)
);

CREATE INDEX idx_race_comparison_lookup
ON race_comparison(race_id, driver_name, lap_number DESC);
            """)
            print("="*60)
            print("\n🌐 Go to: https://supabase.com/dashboard/project/vdgdutmrglygsfmqttxw/sql/new")
            print("   Paste the SQL above and click 'Run'")
            return False

        else:
            print(f"❌ Error accessing table: {error_msg}")
            return False


def test_comparison_data():
    """Check if comparison data exists"""

    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    try:
        response = supabase.table('race_comparison').select('*').eq(
            'race_id', 'monaco_2024'
        ).eq('driver_name', 'LEC').order('lap_number', desc=True).limit(1).execute()

        if response.data and len(response.data) > 0:
            lap = response.data[0]
            print(f"\n✅ Comparison data found for lap {lap['lap_number']}")
            print(f"   AI: {lap['ai_cumulative_time']:.1f}s ({lap['ai_tire_compound']}, age {lap['ai_tire_age']})")
            print(f"   Baseline: {lap['baseline_cumulative_time']:.1f}s ({lap['baseline_tire_compound']}, age {lap['baseline_tire_age']})")
            print(f"   Difference: {lap['time_difference']:.1f}s")
            return True
        else:
            print("\n⚠️  No comparison data yet")
            print("   This is normal if you haven't started race_monitor_v2.py yet")
            return False

    except Exception as e:
        print(f"\n⚠️  Could not check comparison data: {e}")
        return False


if __name__ == '__main__':
    table_exists = test_visualization_setup()

    if table_exists:
        print("\n" + "="*60)
        test_comparison_data()

    print("\n" + "="*60)
    print("\n📍 VISUALIZATION LOCATION:")
    print("   Frontend: http://localhost:5173")
    print("   Component: RaceComparison (top of dashboard)")
    print("   Data source: race_comparison table in Supabase")
    print("\n🚀 TO SEE IT:")
    print("   1. Create race_comparison table (see SQL above)")
    print("   2. Run: python race_monitor_v2.py LEC monaco_2024")
    print("   3. Run: cd ../frontend && npm run dev")
    print("   4. Open: http://localhost:5173")
    print("   5. Look at TOP of page - split-screen race comparison!")
    print("="*60 + "\n")
