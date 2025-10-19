"""
Setup script for race comparison visualization
Creates the race_comparison table in Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def setup_race_comparison_table():
    """Create race_comparison table in Supabase"""

    print("🏗️  Setting up race comparison visualization...")
    print("="*60)

    # Connect to Supabase
    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    # Read SQL file
    with open('create_race_comparison_table.sql', 'r') as f:
        sql = f.read()

    # Execute SQL
    try:
        # Note: Supabase client doesn't have direct SQL execution via Python SDK
        # We'll need to use the SQL editor in Supabase dashboard
        print("⚠️  Cannot execute SQL directly via Python SDK")
        print("\n📋 Please run this SQL in your Supabase SQL Editor:")
        print("="*60)
        print(sql)
        print("="*60)
        print("\nOR use the Supabase CLI:")
        print("supabase db execute < create_race_comparison_table.sql")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

if __name__ == '__main__':
    setup_race_comparison_table()
