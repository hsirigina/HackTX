"""
Manual Pit Stop Override - For Hackathon Demo
Allows triggering pit stops during race replay to test AI strategies
"""

import threading
import time
from pit_stop_simulator import PitStopSimulator

class ManualPitOverride:
    """
    Monitors for manual pit stop commands during race replay
    """

    def __init__(self, race_monitor, pit_simulator: PitStopSimulator):
        """
        Initialize manual override system

        Args:
            race_monitor: RaceMonitorV2 instance
            pit_simulator: PitStopSimulator instance
        """
        self.race_monitor = race_monitor
        self.pit_simulator = pit_simulator
        self.pit_requested = False
        self.listening = False

    def start_listening(self):
        """Start listening for pit stop commands in background thread"""
        self.listening = True
        listener_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        listener_thread.start()
        print("\n💡 Manual Override Active: Press 'P' + ENTER during race to pit")

    def _listen_for_commands(self):
        """Background thread to listen for keyboard input"""
        while self.listening:
            try:
                cmd = input().strip().upper()
                if cmd == 'P':
                    self.pit_requested = True
                    print("\n🔧 PIT STOP QUEUED - Will execute on next lap")
            except:
                pass
            time.sleep(0.1)

    def check_and_execute_pit(self, current_lap: int, driver_number: int, driver_name: str):
        """
        Check if pit stop was requested and execute it

        Args:
            current_lap: Current lap number
            driver_number: Driver number
            driver_name: Driver name

        Returns:
            True if pit stop executed, False otherwise
        """
        if self.pit_requested:
            # Get AI recommendation for tire compound
            last_rec = self.race_monitor.coordinator.get_cached_recommendation()
            compound = last_rec.get('target_compound', 'MEDIUM') if last_rec else 'MEDIUM'

            # Execute pit stop
            self.pit_simulator.execute_pit_stop(
                current_lap=current_lap,
                driver_number=driver_number,
                driver_name=driver_name,
                new_compound=compound
            )

            self.pit_requested = False
            return True

        return False

    def stop_listening(self):
        """Stop listening for commands"""
        self.listening = False


# Example usage in demo_v2.py:
"""
# In demo_v2.py, add after initializing race monitor:

from manual_pit_override import ManualPitOverride
from pit_stop_simulator import PitStopSimulator

# Initialize pit stop simulation
pit_sim = PitStopSimulator(supabase, RACE_ID)
manual_pit = ManualPitOverride(monitor, pit_sim)
manual_pit.start_listening()

# Then in race monitor's _process_lap method, check for manual pit:
if manual_pit.check_and_execute_pit(lap_number, driver_number, driver_name):
    # Modify tire data for this lap
    lap_data['tire_age'] = 0
    lap_data['compound'] = pit_sim.pit_stops_executed[-1]['new_compound']
"""
