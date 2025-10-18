"""
Race Monitor V2 - Event-Based Smart Triggering
Uses 4 data agents + 1 AI coordinator for minimal API calls
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

from data_agents import (
    TireDataAgent,
    LapTimeAgent,
    PositionAgent,
    CompetitorAgent,
    EventDetector,
    TriggerEvent
)
from coordinator_agent import CoordinatorAgent
from arduino_controller import ArduinoController

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


class RaceMonitorV2:
    """
    Race monitor with smart event-based triggering
    Data agents run every lap (free), AI only called when needed
    """

    def __init__(self, driver_name: str, race_id: str, use_arduino: bool = True):
        """
        Initialize race monitor

        Args:
            driver_name: Driver to monitor (e.g., "LEC")
            race_id: Unique race identifier
            use_arduino: Whether to use Arduino display
        """
        self.driver_name = driver_name
        self.race_id = race_id

        # Initialize Supabase
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Initialize data agents (pure Python, free!)
        self.tire_agent = TireDataAgent(driver_name)
        self.lap_time_agent = LapTimeAgent(driver_name)
        self.position_agent = PositionAgent(driver_name)
        self.competitor_agent = CompetitorAgent(driver_name)

        # Initialize event detector
        self.event_detector = EventDetector()

        # Initialize AI coordinator (only called when events trigger it)
        self.coordinator = CoordinatorAgent(driver_name)

        # Initialize Arduino controller
        self.arduino = None
        if use_arduino:
            try:
                self.arduino = ArduinoController()
                print(f"✅ Arduino connected on {self.arduino.port}")
            except Exception as e:
                print(f"⚠️  Arduino not available: {e}")

        # State tracking
        self.last_processed_lap = 0
        self.ai_call_count = 0
        self.total_laps_processed = 0

        print(f"\n{'='*60}")
        print(f"Race Monitor V2 - Smart Event Triggering")
        print(f"{'='*60}")
        print(f"Driver: {driver_name}")
        print(f"Race ID: {race_id}")
        print(f"Architecture: 4 Data Agents + 1 AI Coordinator")
        print(f"{'='*60}\n")

    def monitor(self, poll_interval: float = 1.0, max_laps: Optional[int] = None):
        """
        Monitor race with smart event-based triggering

        Args:
            poll_interval: How often to poll Supabase (seconds)
            max_laps: Optional max laps to process (for testing)
        """
        print(f"🏁 Monitoring {self.driver_name}...")
        print(f"Poll interval: {poll_interval}s")
        print(f"Waiting for lap data...\n")

        try:
            while True:
                # Get latest lap data
                lap_data = self._get_latest_lap_data()

                if lap_data and lap_data['lap_number'] > self.last_processed_lap:
                    self._process_lap(lap_data)

                    # Check if we should stop
                    if max_laps and self.total_laps_processed >= max_laps:
                        print(f"\n✅ Processed {max_laps} laps, stopping.")
                        break

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            self._print_summary()

    def _get_latest_lap_data(self) -> Optional[Dict]:
        """Fetch latest lap data from Supabase"""
        try:
            # Get lap times
            lap_times_response = self.supabase.table('lap_times').select('*').eq(
                'race_id', self.race_id
            ).eq(
                'driver', self.driver_name
            ).order('lap_number', desc=True).limit(10).execute()

            if not lap_times_response.data:
                return None

            latest_lap = lap_times_response.data[0]
            lap_number = latest_lap['lap_number']

            # Get tire data
            tire_response = self.supabase.table('tire_data').select('*').eq(
                'race_id', self.race_id
            ).eq(
                'driver', self.driver_name
            ).eq(
                'lap_number', lap_number
            ).execute()

            # Get position data
            position_response = self.supabase.table('race_positions').select('*').eq(
                'race_id', self.race_id
            ).eq(
                'driver', self.driver_name
            ).eq(
                'lap_number', lap_number
            ).execute()

            # Get all drivers for competitor analysis
            all_drivers_response = self.supabase.table('race_positions').select('*').eq(
                'race_id', self.race_id
            ).eq(
                'lap_number', lap_number
            ).execute()

            # Combine data
            combined = {
                'lap_number': lap_number,
                'lap_time': latest_lap.get('lap_time_seconds'),
                'sector1': latest_lap.get('sector1_seconds'),
                'sector2': latest_lap.get('sector2_seconds'),
                'sector3': latest_lap.get('sector3_seconds'),
                'compound': tire_response.data[0].get('compound') if tire_response.data else None,
                'tire_age': tire_response.data[0].get('tire_age') if tire_response.data else 0,
                'position': position_response.data[0].get('position') if position_response.data else None,
                'gap_ahead': position_response.data[0].get('interval_seconds') if position_response.data else None,
                'all_drivers': all_drivers_response.data if all_drivers_response.data else []
            }

            return combined

        except Exception as e:
            print(f"Error fetching lap data: {e}")
            return None

    def _process_lap(self, lap_data: Dict):
        """
        Process a new lap with event-based triggering

        Args:
            lap_data: Combined lap data from all tables
        """
        lap_number = lap_data['lap_number']
        self.last_processed_lap = lap_number
        self.total_laps_processed += 1

        print(f"\n{'='*60}")
        print(f"📍 LAP {lap_number} - {self.driver_name}")
        print(f"{'='*60}")

        # Print basic info
        print(f"⏱️  Lap time: {lap_data['lap_time']:.3f}s")
        print(f"🏁 Position: P{lap_data.get('position', '?')}")
        print(f"🔧 Tires: {lap_data.get('compound', '?')} ({lap_data.get('tire_age', 0)} laps)")

        # ========================================
        # STEP 1: Run all data agents (FREE!)
        # ========================================
        all_events = []

        # Tire agent
        tire_events = self.tire_agent.analyze(
            lap_data={
                'compound': lap_data.get('compound'),
                'tire_age': lap_data.get('tire_age', 0),
                'lap_time': lap_data.get('lap_time'),
                'track_temp': 30.0
            },
            current_lap=lap_number
        )
        all_events.extend(tire_events)

        # Lap time agent
        if lap_data.get('lap_time'):
            pace_events = self.lap_time_agent.analyze(
                lap_data={
                    'lap_time': lap_data['lap_time'],
                    'sector1': lap_data.get('sector1'),
                    'sector2': lap_data.get('sector2'),
                    'sector3': lap_data.get('sector3')
                },
                current_lap=lap_number
            )
            all_events.extend(pace_events)

        # Position agent
        position_events = self.position_agent.analyze(
            position_data={
                'position': lap_data.get('position'),
                'gap_ahead': lap_data.get('gap_ahead'),
                'gap_behind': self._get_gap_behind(lap_data)
            },
            current_lap=lap_number
        )
        all_events.extend(position_events)

        # Competitor agent
        our_data = {
            'position': lap_data.get('position'),
            'lap_time': lap_data.get('lap_time'),
            'tire_age': lap_data.get('tire_age', 0)
        }
        competitor_events = self.competitor_agent.analyze(
            our_data=our_data,
            all_drivers=self._format_competitors(lap_data['all_drivers']),
            current_lap=lap_number
        )
        all_events.extend(competitor_events)

        # ========================================
        # STEP 2: Check if we should call AI
        # ========================================
        should_call_ai, sorted_events = self.event_detector.check_triggers(all_events)

        # Print detected events
        critical_high = [e for e in sorted_events if e.urgency in ['CRITICAL', 'HIGH']]
        if critical_high:
            print(f"\n🚨 Events Detected:")
            for event in critical_high:
                icon = "🔴" if event.urgency == 'CRITICAL' else "🟡"
                print(f"   {icon} [{event.urgency}] {event.data.get('message', event.type)}")

        # ========================================
        # STEP 3: Call AI if needed (EXPENSIVE!)
        # ========================================
        if should_call_ai:
            print(f"\n🤖 Calling AI Coordinator (API Call #{self.ai_call_count + 1})...")

            # Get position data
            position_data = {
                'position': lap_data.get('position'),
                'gap_ahead': lap_data.get('gap_ahead'),
                'gap_behind': self._get_gap_behind(lap_data)
            }

            # Call coordinator
            recommendation = self.coordinator.analyze_situation(
                current_lap=lap_number,
                events=sorted_events,
                lap_data=lap_data,
                position_data=position_data,
                competitor_data=self._format_competitors(lap_data['all_drivers'])
            )

            self.ai_call_count += 1

            # Display recommendation
            self._display_recommendation(recommendation)

            # Save to database
            self._save_recommendation(lap_number, recommendation)

            # Update Arduino
            self._update_arduino(recommendation)

        else:
            print(f"✅ No AI call needed (using cached strategy)")

            # Still update display with cached recommendation
            cached = self.coordinator.get_cached_recommendation()
            if cached:
                self._update_arduino(cached)

        # Print API efficiency
        if self.total_laps_processed > 0:
            efficiency = (1 - self.ai_call_count / self.total_laps_processed) * 100
            print(f"\n📊 API Efficiency: {self.ai_call_count} calls / {self.total_laps_processed} laps ({efficiency:.1f}% reduction)")

    def _get_gap_behind(self, lap_data: Dict) -> float:
        """Calculate gap to car behind"""
        our_position = lap_data.get('position')
        if not our_position or our_position == 20:
            return 999.0

        all_drivers = lap_data.get('all_drivers', [])
        behind = [d for d in all_drivers if d.get('position') == our_position + 1]

        if behind:
            return behind[0].get('interval_seconds', 999.0)

        return 999.0

    def _format_competitors(self, all_drivers: List[Dict]) -> List[Dict]:
        """Format competitor data for agents"""
        formatted = []

        for driver in all_drivers:
            if driver.get('driver') == self.driver_name:
                continue

            # Get tire data for this driver
            try:
                tire_response = self.supabase.table('tire_data').select('*').eq(
                    'race_id', self.race_id
                ).eq(
                    'driver', driver['driver']
                ).eq(
                    'lap_number', driver['lap_number']
                ).execute()

                tire_age = tire_response.data[0].get('tire_age', 0) if tire_response.data else 0
                compound = tire_response.data[0].get('compound', 'UNKNOWN') if tire_response.data else 'UNKNOWN'
            except:
                tire_age = 0
                compound = 'UNKNOWN'

            # Get lap time
            try:
                lap_response = self.supabase.table('lap_times').select('*').eq(
                    'race_id', self.race_id
                ).eq(
                    'driver', driver['driver']
                ).eq(
                    'lap_number', driver['lap_number']
                ).execute()

                lap_time = lap_response.data[0].get('lap_time_seconds') if lap_response.data else None
            except:
                lap_time = None

            formatted.append({
                'name': driver['driver'],
                'position': driver.get('position'),
                'lap_time': lap_time,
                'tire_age': tire_age,
                'compound': compound
            })

        return formatted

    def _display_recommendation(self, rec: Dict):
        """Display AI recommendation"""
        print(f"\n{'─'*60}")
        print(f"🎯 AI COORDINATOR RECOMMENDATION")
        print(f"{'─'*60}")

        urgency_icons = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠',
            'CRITICAL': '🔴'
        }

        urgency = rec.get('urgency', 'MEDIUM')
        print(f"{urgency_icons.get(urgency, '⚪')} Urgency: {urgency}")
        print(f"📌 Type: {rec.get('recommendation_type', 'UNKNOWN')}")
        print(f"🎲 Confidence: {rec.get('confidence', 0.0):.0%}")

        if rec.get('pit_window'):
            print(f"🔧 Pit window: Laps {rec['pit_window'][0]}-{rec['pit_window'][1]}")

        if rec.get('target_compound'):
            print(f"🏁 Target compound: {rec['target_compound']}")

        print(f"\n📻 Driver: \"{rec.get('driver_instruction', 'N/A')}\"")
        print(f"👷 Pit Crew: \"{rec.get('pit_crew_instruction', 'N/A')}\"")

        print(f"\n💡 Reasoning:")
        print(f"   {rec.get('reasoning', 'N/A')}")

        print(f"{'─'*60}")

    def _save_recommendation(self, lap_number: int, recommendation: Dict):
        """Save recommendation to Supabase"""
        try:
            self.supabase.table('agent_recommendations').insert({
                'race_id': self.race_id,
                'driver': self.driver_name,
                'lap_number': lap_number,
                'agent_type': 'COORDINATOR',
                'recommendation': recommendation,
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"⚠️  Error saving recommendation: {e}")

    def _update_arduino(self, recommendation: Dict):
        """Update Arduino display with recommendation"""
        if not self.arduino:
            return

        try:
            rec_type = recommendation.get('recommendation_type', '')

            if rec_type == 'PIT_NOW':
                self.arduino.pit_now()

            elif rec_type == 'PIT_SOON':
                pit_window = recommendation.get('pit_window', [0, 0])
                laps_until = pit_window[0] - self.last_processed_lap
                if laps_until > 0:
                    self.arduino.set_pit_countdown(laps_until)

            elif rec_type == 'STAY_OUT':
                self.arduino.stay_out()

            elif rec_type in ['PUSH', 'DEFEND']:
                self.arduino.set_message(rec_type)

            elif rec_type == 'CONSERVE':
                self.arduino.set_message('CONSERVE')

        except Exception as e:
            print(f"⚠️  Arduino error: {e}")

    def _print_summary(self):
        """Print monitoring summary"""
        print(f"\n{'='*60}")
        print(f"📊 RACE MONITORING SUMMARY")
        print(f"{'='*60}")
        print(f"Driver: {self.driver_name}")
        print(f"Laps processed: {self.total_laps_processed}")
        print(f"AI API calls: {self.ai_call_count}")

        if self.total_laps_processed > 0:
            efficiency = (1 - self.ai_call_count / self.total_laps_processed) * 100
            print(f"API reduction: {efficiency:.1f}%")

            avg_calls_per_lap = self.ai_call_count / self.total_laps_processed
            print(f"Avg calls per lap: {avg_calls_per_lap:.2f}")

        print(f"{'='*60}\n")


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python race_monitor_v2.py <driver> <race_id>")
        print("Example: python race_monitor_v2.py LEC monaco_2024")
        sys.exit(1)

    driver = sys.argv[1]
    race_id = sys.argv[2]

    monitor = RaceMonitorV2(driver, race_id, use_arduino=True)
    monitor.monitor(poll_interval=1.0)
