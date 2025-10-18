"""
Demo Script - Runs full F1 AI Agent system demonstration.
Starts race replay and agent monitor in coordinated fashion.
"""
import os
import sys
import time
import threading
from dotenv import load_dotenv

# Import our modules
from race_replay import RaceReplay
from race_monitor import RaceMonitor

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


def run_monitor(monitor: RaceMonitor):
    """Run race monitor in main thread."""
    print("\n👀 Starting race monitor...")
    monitor.monitor(poll_interval=1.0)


def main():
    """Main demo entry point."""
    print("=" * 70)
    print("F1 Multi-Agent Race Strategy System - DEMO")
    print("=" * 70)

    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    if not google_api_key or google_api_key == 'your_google_gemini_api_key_here':
        print("\n⚠️  Warning: GOOGLE_API_KEY not set")
        print("   Agents will not work without a valid API key")
        print("   Get free key at: https://aistudio.google.com/app/apikey")
        print("\n   Continue anyway? (y/n): ", end='')

        response = input().strip().lower()
        if response != 'y':
            return

    # Demo configuration
    RACE_ID = "monaco_2024"
    FOCUSED_DRIVER = "LEC"  # Charles Leclerc (winner)
    START_LAP = 60  # Final stint
    END_LAP = 78    # Race end
    LAPS_PER_SECOND = 0.5  # 1 lap every 2 seconds

    print(f"\nDemo Configuration:")
    print(f"  Race: Monaco 2024")
    print(f"  Focused Driver: {FOCUSED_DRIVER} (Charles Leclerc)")
    print(f"  Laps: {START_LAP} to {END_LAP}")
    print(f"  Replay Speed: {LAPS_PER_SECOND} laps/second")
    print(f"\nThis demo shows the final 19 laps where Leclerc")
    print(f"held off Piastri to win his home race!")

    # Initialize replay
    print(f"\n{'='*70}")
    print("SETUP PHASE")
    print(f"{'='*70}")

    replay = RaceReplay(
        race_id=RACE_ID,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        laps_per_second=LAPS_PER_SECOND
    )

    # Load race data
    replay.load_race(2024, 'Monaco', 'R')

    # Clear old data
    replay.clear_race_data()

    # Initialize monitor
    monitor = RaceMonitor(
        race_id=RACE_ID,
        focused_driver=FOCUSED_DRIVER,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )

    # Start demo
    print(f"\n{'='*70}")
    print("DEMO STARTING")
    print(f"{'='*70}")
    print("\nThe system will:")
    print("  1. Stream race data lap-by-lap to Supabase")
    print("  2. AI agents monitor and analyze each lap")
    print("  3. Generate strategic recommendations")
    print(f"\nPress Ctrl+C to stop the demo\n")

    time.sleep(2)

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
        print(f"\n\n{'='*70}")
        print("DEMO STOPPED")
        print(f"{'='*70}")
        print(f"Analyzed {monitor.last_processed_lap - START_LAP + 1} laps")
        print("\nThank you for watching the demo!")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()
