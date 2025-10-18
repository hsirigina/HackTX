"""
Arduino Driver Display Controller
Controls the Arduino LCD display via serial communication.
"""
import serial
import serial.tools.list_ports
import time
from typing import Optional


class ArduinoController:
    """Controls Arduino driver display via serial."""

    def __init__(self, port: Optional[str] = None, baud: int = 9600):
        """
        Initialize Arduino controller.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0', 'COM3')
                  If None, will try to auto-detect Arduino
            baud: Baud rate (default 9600)
        """
        self.port = port or self._auto_detect_arduino()
        self.baud = baud
        self.ser = None

        if self.port:
            self._connect()
        else:
            print("⚠️  No Arduino detected. Display commands will be logged only.")

    def _auto_detect_arduino(self) -> Optional[str]:
        """Auto-detect Arduino on serial ports."""
        ports = serial.tools.list_ports.comports()

        for port in ports:
            # Look for Arduino
            if 'Arduino' in port.description or 'USB Serial' in port.description:
                print(f"✓ Found Arduino on {port.device}")
                return port.device

        return None

    def _connect(self):
        """Connect to Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            print(f"✓ Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            print(f"⚠️  Could not connect to Arduino: {e}")
            self.ser = None

    def send_command(self, command: str, value: str = ""):
        """
        Send command to Arduino.

        Args:
            command: Command name
            value: Command value
        """
        if value:
            msg = f"{command}:{value}\n"
        else:
            msg = f"{command}\n"

        if self.ser and self.ser.is_open:
            try:
                self.ser.write(msg.encode())
                print(f"  → Arduino: {msg.strip()}")
            except serial.SerialException as e:
                print(f"⚠️  Serial error: {e}")
        else:
            print(f"  → Arduino (offline): {msg.strip()}")

    # Convenience methods
    def update_lap(self, current: int, total: int):
        """Update lap counter."""
        self.send_command("LAP", f"{current}/{total}")

    def update_position(self, position: int):
        """Update driver position."""
        self.send_command("POSITION", str(position))

    def update_gap(self, gap: float):
        """Update gap to car behind/ahead."""
        sign = "+" if gap >= 0 else ""
        self.send_command("GAP", f"{sign}{gap:.1f}")

    def set_tire_status(self, status: str):
        """Set tire status: OK, WARN, or CRITICAL."""
        self.send_command("TIRE_STATUS", status)

    def set_strategy(self, strategy_id: str):
        """Set current strategy (A, B, C, etc.)."""
        self.send_command("STRATEGY", strategy_id)

    def set_pit_countdown(self, laps: int):
        """Set pit countdown timer."""
        self.send_command("PIT_COUNTDOWN", str(laps))

    def pit_now(self):
        """Trigger urgent pit now alert."""
        self.send_command("URGENT", "PIT_NOW")

    def stay_out(self):
        """Trigger stay out alert (cancel pit)."""
        self.send_command("URGENT", "STAY_OUT")

    def analyzing(self):
        """Show team analyzing status."""
        self.send_command("URGENT", "ANALYZE")

    def clear(self):
        """Return to normal monitoring."""
        self.send_command("CLEAR")

    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("✓ Arduino connection closed")


# Demo/Test script
if __name__ == "__main__":
    print("=" * 60)
    print("Arduino Driver Display Test")
    print("=" * 60)

    # Initialize controller
    arduino = ArduinoController()

    if not arduino.ser:
        print("\n⚠️  No Arduino connected. Running in simulation mode.")
        print("Commands will be printed but not sent to hardware.\n")

    # Simulate race sequence
    print("\n🎬 Simulating race sequence...\n")

    # Normal racing
    print("1. Normal racing")
    arduino.update_lap(10, 78)
    arduino.update_position(2)
    arduino.update_gap(1.2)
    arduino.set_tire_status("OK")
    time.sleep(3)

    # Pit strategy decided
    print("\n2. Pit strategy decided")
    arduino.set_strategy("A")
    arduino.set_pit_countdown(5)
    time.sleep(2)

    # Countdown
    print("\n3. Countdown to pit")
    for i in range(5, 0, -1):
        arduino.set_pit_countdown(i)
        time.sleep(2)

    # Pit now
    print("\n4. Pit window open")
    arduino.pit_now()
    time.sleep(3)

    # Back to racing
    print("\n5. Back to racing")
    arduino.clear()
    arduino.update_lap(16, 78)
    time.sleep(2)

    # Close connection
    arduino.close()

    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
