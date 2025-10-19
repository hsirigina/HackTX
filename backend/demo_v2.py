"""
Demo Script V2 - Runs new architecture with 4 Data Agents + 1 AI Coordinator
Demonstrates smart event-based triggering with minimal API calls
"""
import os
import sys
import time
import threading
from dotenv import load_dotenv

# Import our modules
from race_replay import RaceReplay
from race_monitor_v2 import RaceMonitorV2

load_dotenv()


def run_replay(replay: RaceReplay, start_lap: int, end_lap: int, focused_driver: str):
    """Run race replay in a separate thread."""
    print("\n🎬 Starting race replay...")
    time.sleep(2)  # Give monitor time to start
    replay.replay(
        start_lap=start_lap,
        end_lap=end_lap,
        focused_driver=focused_driver
    )
    print("\n✅ Replay complete!")


def run_monitor(monitor: RaceMonitorV2):
    """Run race monitor in main thread."""
    print("\n👀 Starting race monitor...")
    monitor.monitor(poll_interval=1.0)


def main():
    """Main demo entry point."""
    print("=" * 70)
    print("F1 Multi-Agent Race Strategy System V2 - DEMO")
    print("=" * 70)
    print("Architecture: 4 Data Agents (Free) + 1 AI Coordinator (Smart Triggers)")
    print("=" * 70)

    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    if not google_api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not set - AI features will not work")
        print("Get a free key at: https://aistudio.google.com/app/apikey")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    # Demo configuration
    print("\n📋 Demo Configuration:")
    print("   Race: Monaco 2024")
    print("   Driver: Charles Leclerc (LEC)")
    print("   Laps: 60-78 (Final 18 laps - exciting finish!)")
    print("   Speed: 3 seconds per lap\n")

    # Configuration
    YEAR = 2024
    RACE_NAME = "Monaco"
    RACE_ID = "monaco_2024"
    FOCUSED_DRIVER = "LEC"  # Charles Leclerc
    START_LAP = 60
    END_LAP = 78

    # Initialize race replay
    print("\n🔧 Initializing race replay system...")
    replay = RaceReplay(
        race_id=RACE_ID,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        laps_per_second=1/3  # 1 lap every 3 seconds
    )

    # Load Monaco 2024 race data
    replay.load_race(year=YEAR, race_name=RACE_NAME)

    # Clear old race data from Supabase
    replay.clear_race_data()

    # Initialize race monitor V2
    print("🔧 Initializing race monitor V2 (event-based triggering)...")
    monitor = RaceMonitorV2(
        driver_name=FOCUSED_DRIVER,
        race_id=RACE_ID,
        use_arduino=True  # Will auto-detect
    )

    print("\n✅ System ready!\n")

    # Ask user to confirm
    input("Press ENTER to start the demo...")

    # Run replay in background thread
    replay_thread = threading.Thread(
        target=run_replay,
        args=(replay, START_LAP, END_LAP, FOCUSED_DRIVER),
        daemon=True
    )
    replay_thread.start()

    # Run monitor in main thread (so Ctrl+C works)
    try:
        run_monitor(monitor)
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")

    # Wait for replay to finish
    replay_thread.join(timeout=5)

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Achievements:")
    print("  ✅ 4 Data Agents running every lap (free Python analysis)")
    print("  ✅ Smart event-based triggering (only call AI when needed)")
    print("  ✅ Expected: ~8-12 API calls for 18 laps (85%+ reduction)")
    print("  ✅ Real-time strategy recommendations")
    print("  ✅ Arduino display integration (if connected)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
