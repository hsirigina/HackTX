"""
Initialize race_comparison table using Supabase REST API workaround
Since we can't execute DDL directly, we'll insert a dummy record to let Supabase auto-create the table structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def init_race_comparison_table():
    """
    Try to create race_comparison table structure
    """
    print("\n🏗️  Initializing race comparison visualization...")
    print("="*60)

    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    # Check if table exists
    try:
        response = supabase.table('race_comparison').select('*').limit(1).execute()
        print("✅ race_comparison table already exists!")
        return True
    except Exception as e:
        error_msg = str(e)

        if 'does not exist' in error_msg:
            print("❌ Table does not exist - need to create it manually")
            print("\n" + "="*60)
            print("MANUAL SETUP REQUIRED:")
            print("="*60)
            print("\n1. Go to Supabase Dashboard:")
            print("   https://supabase.com/dashboard/project/vdgdutmrglygsfmqttxw/editor")

            print("\n2. Click 'New table' button")

            print("\n3. Set table name: race_comparison")

            print("\n4. Add these columns:")
            print("   - race_id (text, not null)")
            print("   - driver_name (text, not null)")
            print("   - lap_number (int4, not null)")
            print("   - ai_cumulative_time (float8, not null)")
            print("   - ai_tire_compound (text, not null)")
            print("   - ai_tire_age (int4, not null)")
            print("   - ai_has_pitted (bool, default false)")
            print("   - ai_pit_lap (int4, nullable)")
            print("   - baseline_cumulative_time (float8, not null)")
            print("   - baseline_tire_compound (text, not null)")
            print("   - baseline_tire_age (int4, not null)")
            print("   - baseline_has_pitted (bool, default false)")
            print("   - baseline_pit_lap (int4, nullable)")
            print("   - time_difference (float8, nullable)")

            print("\n5. Click 'Save'")

            print("\n6. Then run this script again to verify")

            print("\n" + "="*60)
            print("\nOR use SQL Editor:")
            print("https://supabase.com/dashboard/project/vdgdutmrglygsfmqttxw/sql/new")
            print("\nPaste this SQL:")
            print("="*60)
            with open('create_race_comparison_table.sql', 'r') as f:
                print(f.read())
            print("="*60)

            return False
        else:
            print(f"❌ Error: {error_msg}")
            return False


if __name__ == '__main__':
    success = init_race_comparison_table()

    if success:
        print("\n✅ Visualization is ready!")
        print("\n🚀 Next steps:")
        print("   1. Run: python race_monitor_v2.py LEC monaco_2024")
        print("   2. Run: cd ../frontend && npm run dev")
        print("   3. Open: http://localhost:5173")
        print("   4. Look at the TOP of the page for split-screen comparison!")
    else:
        print("\n⏸️  Complete the manual setup above, then re-run this script")
