# Product Requirements Document: Arduino Driver Display System

## Overview

A physical driver alert system that displays real-time pit strategy information on an Arduino-powered LCD/OLED screen, providing F1 drivers with persistent visual alerts as a backup to radio communication.

## Problem Statement

F1 drivers rely on radio communication from race engineers for pit strategy instructions. However:
- Drivers can miss radio calls during intense wheel-to-wheel racing
- Audio can be garbled or lost due to technical issues
- Split-second decisions require persistent visual reference
- Mental calculation of pit timing adds cognitive load during high-pressure moments

## Solution

An Arduino-based driver display mounted in sight line that shows:
- Countdown to pit stop (laps remaining)
- Current strategy selection (A/B/C)
- Urgent alerts ("PIT NOW - BOX BOX BOX")
- Strategy changes in real-time
- Team analysis status

## Goals

### Primary Goals
1. Provide redundant communication channel between pit wall and driver
2. Reduce driver cognitive load with persistent visual information
3. Eliminate missed pit calls due to radio issues or driver focus
4. Create compelling physical demo element for hackathon presentation

### Secondary Goals
1. Demonstrate full-stack hardware integration capability
2. Show end-to-end system (agents → dashboard → driver)
3. Make demo visually engaging with physical component

## Non-Goals

- Not replacing radio communication (supplement only)
- Not providing detailed telemetry data to driver (steering wheel handles that)
- Not building actual in-car F1 hardware (mockup for demo)
- Not waterproofing or ruggedizing for real racing conditions

## Hardware Requirements

### Required Components

**Arduino Board:**
- Arduino Uno R3 **OR** Arduino Nano
- Recommendation: Nano (smaller, easier to mount)

**Display:**
- **Option A:** 16x2 LCD with I2C module (easier, cheaper)
- **Option B:** 128x64 OLED display (sharper, more modern look)
- Recommendation: 16x2 LCD for hackathon (simpler wiring, larger text)

**Connection:**
- USB-A to USB-B cable (Uno) or USB-A to Mini-USB (Nano)
- Minimum 3ft length for demo setup

**Optional Components:**
- Piezo buzzer (audio alerts)
- 220Ω resistor for LCD backlight control
- Breadboard and jumper wires
- Enclosure/case for clean look

### Physical Setup

**Mockup Steering Wheel:**
- 3D printed or cardboard steering wheel mockup
- Display mounted at top (12 o'clock position)
- Driver can glance without moving head
- Alternative: Standalone display on adjustable stand

**Positioning Requirements:**
- Eye level or slightly below
- Within 45° viewing angle from forward gaze
- Readable from 12-18 inches distance
- Stable mount (no wobbling during demo)

## Display States & Content

### State 1: Normal Monitoring
**When:** Race ongoing, no immediate strategy changes
**Display:**
```
┌──────────────────┐
│ LAP 15/58  P1    │  <- Current lap / Total laps, Position
│ TIRES OK    +2.3 │  <- Tire status, Gap to car behind
└──────────────────┘
```
**Updates:** Every lap

### State 2: Pit Window Approaching
**When:** Coordinator locks in pit strategy, window 2+ laps away
**Display:**
```
┌──────────────────┐
│ LAPS TO PIT: 5   │  <- Countdown timer
│ STRATEGY: A      │  <- Strategy ID (A/B/C)
└──────────────────┘
```
**Updates:** Every lap (countdown decrements)

### State 3: Pit Window Imminent
**When:** 1 lap before pit stop
**Display:**
```
┌──────────────────┐
│ LAPS TO PIT: 1   │  <- Flashing text
│ PREPARE TO BOX   │  <- Warning message
└──────────────────┘
```
**Behavior:**
- Text flashes every 500ms (inverted colors)
- Optional: Buzzer beep pattern (single beep every 2 seconds)

### State 4: Pit Now (Urgent)
**When:** Pit entry lap
**Display:**
```
┌──────────────────┐
│ >>> PIT NOW <<<  │  <- Centered, flashing rapidly
│ BOX BOX BOX      │  <- Standard F1 pit call phrase
└──────────────────┘
```
**Behavior:**
- Rapid flashing (200ms interval)
- Maximum brightness
- Optional: Continuous buzzer tone (if equipped)

### State 5: Stay Out (Override)
**When:** Strategy changes, pit cancelled
**Display:**
```
┌──────────────────┐
│ STAY OUT! STAY   │  <- Override message
│ OUT! NO PIT      │  <- Emphasis
└──────────────────┘
```
**Behavior:**
- Flash 3 times, then stay solid
- Different tone pattern (if buzzer equipped)

### State 6: Strategy Update
**When:** Conditions change (rain, safety car, etc.)
**Display:**
```
┌──────────────────┐
│ STRATEGY UPDATE! │  <- Alert line
│ NEW: B  OLD: A   │  <- Show change
└──────────────────┘
```
**Behavior:**
- Display for 5 seconds
- Then transition to new strategy countdown

### State 7: Agent Debate
**When:** Coordinator agents disagree, analyzing options
**Display:**
```
┌──────────────────┐
│ TEAM ANALYZING.. │  <- Team working message
│ STAND BY         │  <- Wait instruction
└──────────────────┘
```
**Behavior:**
- Dots animate (...) to show activity
- Remains until decision locked

## Serial Communication Protocol

### Connection Specifications
- **Baud Rate:** 9600
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1
- **Flow Control:** None

### Command Format
```
COMMAND:VALUE\n
```

All commands terminated with newline character (`\n`).

### Command Reference

| Command | Value | Example | Description |
|---------|-------|---------|-------------|
| `STATUS` | `OK`, `WARNING`, `CRITICAL` | `STATUS:OK\n` | Set overall status indicator |
| `LAP` | Current/Total (e.g., `15/58`) | `LAP:15/58\n` | Update lap counter |
| `POSITION` | Integer 1-20 | `POSITION:1\n` | Update driver position |
| `GAP` | Float (seconds, can be negative) | `GAP:+2.3\n` | Gap to car behind (+ or -) |
| `TIRE_STATUS` | `OK`, `WARN`, `CRITICAL` | `TIRE_STATUS:OK\n` | Tire health indicator |
| `PIT_COUNTDOWN` | Integer (laps) | `PIT_COUNTDOWN:3\n` | Start/update pit countdown |
| `STRATEGY` | String (A/B/C) | `STRATEGY:A\n` | Current strategy ID |
| `URGENT` | `PIT_NOW`, `STAY_OUT`, `ANALYZE` | `URGENT:PIT_NOW\n` | Trigger urgent state |
| `UPDATE` | `OLD:X,NEW:Y` | `UPDATE:OLD:A,NEW:B\n` | Strategy change |
| `CLEAR` | (none) | `CLEAR\n` | Return to normal monitoring |

### Example Command Sequence

**Scenario: Normal race → Pit window → Pit execution**

```
1. LAP:10/58\n
2. POSITION:2\n
3. GAP:+1.2\n
4. TIRE_STATUS:OK\n
   → Display: Normal monitoring

5. STRATEGY:A\n
6. PIT_COUNTDOWN:5\n
   → Display: Pit window approaching

7. PIT_COUNTDOWN:4\n
8. PIT_COUNTDOWN:3\n
9. PIT_COUNTDOWN:2\n
   → Display: Countdown updates each lap

10. PIT_COUNTDOWN:1\n
    → Display: Pit window imminent (flashing)

11. URGENT:PIT_NOW\n
    → Display: Pit now (rapid flashing)

12. CLEAR\n
13. LAP:16/58\n
    → Display: Return to normal monitoring
```

### Error Handling

**Invalid Command:**
- Arduino ignores command
- Continues displaying last valid state
- Optional: Send `ERROR\n` back to backend (for debugging)

**Connection Lost:**
- Display shows last known state
- After 30 seconds of no data: Show `CONNECTION LOST`
- Auto-reconnect when serial resumes

**Malformed Data:**
- Ignore packet
- Wait for next valid command

## Arduino Software Architecture

### Libraries Required
```cpp
#include <Wire.h>           // I2C communication
#include <LiquidCrystal_I2C.h>  // LCD control (if using LCD)
// OR
#include <Adafruit_GFX.h>   // Graphics library (if using OLED)
#include <Adafruit_SSD1306.h>  // OLED control
```

### State Machine

```cpp
enum DisplayState {
  STATE_MONITORING,      // Normal race info
  STATE_PIT_COUNTDOWN,   // Pit window approaching
  STATE_PIT_IMMINENT,    // 1 lap before pit
  STATE_PIT_NOW,         // Urgent pit call
  STATE_STAY_OUT,        // Override, no pit
  STATE_STRATEGY_UPDATE, // Strategy changed
  STATE_ANALYZING        // Team debating
};

DisplayState currentState = STATE_MONITORING;
```

### Main Loop Logic
```cpp
void loop() {
  // 1. Check for serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  // 2. Update display based on state
  updateDisplay();

  // 3. Handle flashing/animations
  if (shouldFlash()) {
    toggleDisplay();
  }

  // 4. Update buzzer if equipped
  updateBuzzer();

  delay(50);  // 20Hz update rate
}
```

### Display Update Function
```cpp
void updateDisplay() {
  lcd.clear();

  switch (currentState) {
    case STATE_MONITORING:
      lcd.setCursor(0, 0);
      lcd.print("LAP " + String(currentLap) + "/" + String(totalLaps) + "  P" + String(position));
      lcd.setCursor(0, 1);
      lcd.print("TIRES " + tireStatus + "  " + gap);
      break;

    case STATE_PIT_COUNTDOWN:
      lcd.setCursor(0, 0);
      lcd.print("LAPS TO PIT: " + String(pitCountdown));
      lcd.setCursor(0, 1);
      lcd.print("STRATEGY: " + strategy);
      break;

    case STATE_PIT_NOW:
      if (flashState) {  // Flashing animation
        lcd.setCursor(0, 0);
        lcd.print(">>> PIT NOW <<<");
        lcd.setCursor(0, 1);
        lcd.print("BOX BOX BOX");
      }
      break;

    // ... other states
  }
}
```

### Command Processing
```cpp
void processCommand(String cmd) {
  int separatorIndex = cmd.indexOf(':');
  if (separatorIndex == -1) return;  // Invalid format

  String command = cmd.substring(0, separatorIndex);
  String value = cmd.substring(separatorIndex + 1);

  if (command == "PIT_COUNTDOWN") {
    pitCountdown = value.toInt();
    if (pitCountdown == 1) {
      currentState = STATE_PIT_IMMINENT;
    } else if (pitCountdown > 1) {
      currentState = STATE_PIT_COUNTDOWN;
    }
  }
  else if (command == "URGENT") {
    if (value == "PIT_NOW") {
      currentState = STATE_PIT_NOW;
    }
    else if (value == "STAY_OUT") {
      currentState = STATE_STAY_OUT;
    }
    else if (value == "ANALYZE") {
      currentState = STATE_ANALYZING;
    }
  }
  else if (command == "STRATEGY") {
    strategy = value;
  }
  // ... other commands
}
```

## Backend Integration (Python)

### Serial Connection Setup
```python
import serial
import time

class DriverDisplay:
    def __init__(self, port='/dev/ttyUSB0', baud=9600):
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # Wait for Arduino reset

    def send_command(self, command: str, value: str = ""):
        if value:
            msg = f"{command}:{value}\n"
        else:
            msg = f"{command}\n"
        self.ser.write(msg.encode())

    def update_lap(self, current: int, total: int):
        self.send_command("LAP", f"{current}/{total}")

    def set_pit_countdown(self, laps: int):
        self.send_command("PIT_COUNTDOWN", str(laps))

    def urgent_pit_now(self):
        self.send_command("URGENT", "PIT_NOW")

    def urgent_stay_out(self):
        self.send_command("URGENT", "STAY_OUT")

    def close(self):
        self.ser.close()
```

### Integration with Coordinator Agent
```python
# When Coordinator makes decision
def coordinator_decision_callback(strategy):
    if strategy['action'] == 'PIT':
        pit_lap = strategy['recommended_lap']
        current_lap = race_state['current_lap']
        laps_until_pit = pit_lap - current_lap

        # Update driver display
        driver_display.send_command("STRATEGY", strategy['id'])
        driver_display.set_pit_countdown(laps_until_pit)

    elif strategy['action'] == 'STAY_OUT':
        driver_display.urgent_stay_out()

# Every lap update
def on_lap_update(lap_data):
    driver_display.update_lap(lap_data['current'], lap_data['total'])
    driver_display.send_command("POSITION", str(lap_data['position']))
    driver_display.send_command("GAP", f"+{lap_data['gap']:.1f}")

    # Decrement pit countdown if active
    if pit_countdown_active:
        remaining = pit_lap - lap_data['current']
        if remaining == 0:
            driver_display.urgent_pit_now()
        elif remaining > 0:
            driver_display.set_pit_countdown(remaining)
```

## Wiring Diagram

### 16x2 LCD with I2C Module

```
Arduino Nano          I2C LCD Module
    5V    ────────────── VCC
    GND   ────────────── GND
    A4    ────────────── SDA
    A5    ────────────── SCL

Optional: Piezo Buzzer
    D9    ────────────── Buzzer (+)
    GND   ────────────── Buzzer (-)
```

### 128x64 OLED Display

```
Arduino Nano          OLED Display
    5V    ────────────── VCC
    GND   ────────────── GND
    A4    ────────────── SDA
    A5    ────────────── SCL
```

**Note:** I2C uses same pins (A4/A5) for both display types, making swapping easy.

## Testing Plan

### Unit Tests (Arduino)

**Test 1: Serial Communication**
- Send each command type
- Verify correct state change
- Check display updates

**Test 2: State Transitions**
- Normal → Pit Countdown → Pit Imminent → Pit Now
- Verify each state displays correctly
- Check timing of transitions

**Test 3: Flashing Animation**
- Verify flash rates (imminent: 500ms, urgent: 200ms)
- Check readability during flash
- Test different lighting conditions

**Test 4: Error Handling**
- Send invalid commands
- Disconnect/reconnect serial
- Verify graceful degradation

### Integration Tests (End-to-End)

**Test 5: Full Demo Sequence**
1. Start race replay
2. Agents analyze, make decision
3. Dashboard updates
4. Engineer confirms with gesture
5. Driver display shows countdown → urgent alert
6. Verify timing matches race replay

**Test 6: Strategy Change Mid-Countdown**
- Start pit countdown
- Send strategy change command
- Verify display updates correctly
- Check no state confusion

**Test 7: Multiple Rapid Commands**
- Send commands faster than display update rate
- Verify Arduino doesn't crash
- Check last command wins (correct behavior)

### Demo Day Testing

**Pre-Demo Checklist:**
- [ ] Arduino powered on, serial connected
- [ ] Display brightness optimized for venue lighting
- [ ] Mockup steering wheel stable
- [ ] USB cable secure (tape down if needed)
- [ ] Spare Arduino + cables in backpack
- [ ] Test full demo sequence 3 times
- [ ] Verify display readable from 6 feet (judge distance)

## Bill of Materials (BOM)

| Component | Quantity | Est. Cost | Supplier | Notes |
|-----------|----------|-----------|----------|-------|
| Arduino Nano | 1 | $5-10 | Amazon, AliExpress | Clone is fine |
| 16x2 LCD with I2C | 1 | $5-8 | Amazon | Blue backlight recommended |
| USB-A to Mini-USB cable | 1 | $3-5 | Amazon | 3ft minimum |
| Breadboard (optional) | 1 | $3 | Amazon | If not using direct I2C connection |
| Jumper wires (optional) | 4 | $2 | Amazon | May not need if I2C module pre-wired |
| Piezo buzzer (optional) | 1 | $1-2 | Amazon | 5V active buzzer |
| Enclosure/case (optional) | 1 | $5-10 | 3D print or Amazon | Cleaner look |
| **TOTAL** | | **$15-30** | | Without optional components: $13-18 |

## Timeline

### Hour 1: Hardware Setup
- Unbox Arduino and LCD
- Wire I2C connections (4 wires)
- Upload "Hello World" sketch
- Verify display works

### Hour 2: Basic Arduino Software
- Implement state machine
- Write display update functions
- Test state transitions manually

### Hour 3: Serial Communication
- Implement command parser
- Test commands via Serial Monitor
- Add error handling

### Hour 4: Python Integration
- Write DriverDisplay Python class
- Test sending commands from laptop
- Verify Arduino receives and displays

### Hour 5: Backend Integration
- Connect to Coordinator Agent decisions
- Hook up to lap update events
- Test with race replay

### Hour 6: Physical Mockup
- Build/acquire steering wheel mockup
- Mount display securely
- Optimize viewing angle

### Hour 7: Testing & Polish
- Run full demo sequence
- Fix any bugs or timing issues
- Optimize display text for readability

### Hour 8: Contingency Buffer
- Final testing
- Prepare backup hardware
- Practice demo narrative

**Total: 8 hours** (can be parallelized with other hackathon tasks)

## Success Criteria

### Must-Have (MVP)
- [ ] Display shows pit countdown correctly
- [ ] "PIT NOW" state flashes urgently
- [ ] Serial commands work reliably
- [ ] Display updates within 200ms of command
- [ ] Readable from 4+ feet away
- [ ] Works for 90-second demo without crashes

### Nice-to-Have
- [ ] Buzzer audio alerts
- [ ] All 7 display states implemented
- [ ] Strategy change animations
- [ ] Professional-looking enclosure
- [ ] Multiple demo scenarios programmed

### Demo Impact Goals
- [ ] Judges can clearly see display during demo
- [ ] Adds "wow factor" to presentation
- [ ] Completes pit-wall-to-driver narrative
- [ ] Demonstrates hardware integration skill

## Risk Mitigation

### Risk 1: Display not readable in venue lighting
**Mitigation:**
- Test in bright lighting beforehand
- Adjust backlight brightness in code
- Bring diffuser (white paper) to reduce glare
- Backup: Project display on laptop screen as well

### Risk 2: Serial connection unstable
**Mitigation:**
- Use high-quality USB cable
- Tape down connections
- Implement auto-reconnect in Python
- Backup: Pre-programmed demo sequence on Arduino (no serial needed)

### Risk 3: Arduino crashes during demo
**Mitigation:**
- Extensive testing beforehand
- Add watchdog timer to auto-reset
- Keep spare programmed Arduino ready
- Backup: Video recording of working display

### Risk 4: Display mount falls over
**Mitigation:**
- Test stability before demo
- Use heavy base or clamps
- Tape to table if needed
- Backup: Hand-hold display (less professional but functional)

## Future Enhancements (Post-Hackathon)

### Phase 2 Features
- Multi-color backlight (green/yellow/red for urgency)
- Larger OLED display (2.4" or 3.2")
- Wireless communication (Bluetooth/WiFi instead of USB)
- Battery power for portable demo

### Phase 3 Features
- Driver input buttons (acknowledge pit call)
- Two-way communication (driver can request info)
- Graphical display of race map
- Integration with sim racing setup (iRacing, F1 game)

### Production Considerations (If Building Real Product)
- Ruggedized enclosure (vibration, heat resistant)
- Automotive-grade components
- Integration with actual F1 telemetry systems
- FIA safety certification

## Appendix A: Arduino Sketch Template

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize LCD (address 0x27 or 0x3F, 16 columns, 2 rows)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// State machine
enum DisplayState {
  STATE_MONITORING,
  STATE_PIT_COUNTDOWN,
  STATE_PIT_IMMINENT,
  STATE_PIT_NOW,
  STATE_STAY_OUT,
  STATE_ANALYZING
};

DisplayState currentState = STATE_MONITORING;

// Race data
int currentLap = 0;
int totalLaps = 0;
int position = 0;
String gap = "+0.0";
String tireStatus = "OK";
String strategy = "A";
int pitCountdown = 0;

// Flashing animation
bool flashState = false;
unsigned long lastFlashTime = 0;
int flashInterval = 500;  // ms

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("F1 DRIVER ALERT");
  lcd.setCursor(0, 1);
  lcd.print("SYSTEM READY");
  delay(2000);
  lcd.clear();
}

void loop() {
  // Read serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  // Update display
  updateDisplay();

  // Handle flashing
  if (currentState == STATE_PIT_IMMINENT || currentState == STATE_PIT_NOW) {
    unsigned long now = millis();
    if (now - lastFlashTime > flashInterval) {
      flashState = !flashState;
      lastFlashTime = now;
    }
  }

  delay(50);
}

void processCommand(String cmd) {
  int separatorIndex = cmd.indexOf(':');
  if (separatorIndex == -1) return;

  String command = cmd.substring(0, separatorIndex);
  String value = cmd.substring(separatorIndex + 1);

  if (command == "LAP") {
    int slashIndex = value.indexOf('/');
    currentLap = value.substring(0, slashIndex).toInt();
    totalLaps = value.substring(slashIndex + 1).toInt();
  }
  else if (command == "POSITION") {
    position = value.toInt();
  }
  else if (command == "GAP") {
    gap = value;
  }
  else if (command == "TIRE_STATUS") {
    tireStatus = value;
  }
  else if (command == "STRATEGY") {
    strategy = value;
  }
  else if (command == "PIT_COUNTDOWN") {
    pitCountdown = value.toInt();
    if (pitCountdown == 1) {
      currentState = STATE_PIT_IMMINENT;
      flashInterval = 500;
    } else if (pitCountdown > 1) {
      currentState = STATE_PIT_COUNTDOWN;
    }
  }
  else if (command == "URGENT") {
    if (value == "PIT_NOW") {
      currentState = STATE_PIT_NOW;
      flashInterval = 200;
    }
    else if (value == "STAY_OUT") {
      currentState = STATE_STAY_OUT;
    }
    else if (value == "ANALYZE") {
      currentState = STATE_ANALYZING;
    }
  }
  else if (command == "CLEAR") {
    currentState = STATE_MONITORING;
  }
}

void updateDisplay() {
  lcd.clear();

  switch (currentState) {
    case STATE_MONITORING:
      lcd.setCursor(0, 0);
      lcd.print("LAP ");
      lcd.print(currentLap);
      lcd.print("/");
      lcd.print(totalLaps);
      lcd.print("  P");
      lcd.print(position);

      lcd.setCursor(0, 1);
      lcd.print("TIRES ");
      lcd.print(tireStatus);
      lcd.print(" ");
      lcd.print(gap);
      break;

    case STATE_PIT_COUNTDOWN:
      lcd.setCursor(0, 0);
      lcd.print("LAPS TO PIT: ");
      lcd.print(pitCountdown);

      lcd.setCursor(0, 1);
      lcd.print("STRATEGY: ");
      lcd.print(strategy);
      break;

    case STATE_PIT_IMMINENT:
      if (flashState) {
        lcd.setCursor(0, 0);
        lcd.print("LAPS TO PIT: 1");
        lcd.setCursor(0, 1);
        lcd.print("PREPARE TO BOX");
      }
      break;

    case STATE_PIT_NOW:
      if (flashState) {
        lcd.setCursor(0, 0);
        lcd.print(">>> PIT NOW <<<");
        lcd.setCursor(0, 1);
        lcd.print("BOX BOX BOX");
      }
      break;

    case STATE_STAY_OUT:
      lcd.setCursor(0, 0);
      lcd.print("STAY OUT! STAY");
      lcd.setCursor(0, 1);
      lcd.print("OUT! NO PIT");
      break;

    case STATE_ANALYZING:
      lcd.setCursor(0, 0);
      lcd.print("TEAM ANALYZING..");
      lcd.setCursor(0, 1);
      lcd.print("STAND BY");
      break;
  }
}
```

## Appendix B: Python Integration Example

```python
import serial
import time
from typing import Optional

class DriverDisplay:
    """Interface for Arduino driver display."""

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 9600):
        """
        Initialize driver display connection.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM3' on Windows)
            baud: Baud rate (default 9600)
        """
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            print(f"Driver display connected on {port}")
        except serial.SerialException as e:
            print(f"Failed to connect to driver display: {e}")
            self.ser = None

    def send_command(self, command: str, value: str = ""):
        """Send command to Arduino."""
        if not self.ser:
            return

        try:
            if value:
                msg = f"{command}:{value}\n"
            else:
                msg = f"{command}\n"
            self.ser.write(msg.encode())
            print(f"Sent: {msg.strip()}")
        except serial.SerialException as e:
            print(f"Error sending command: {e}")

    # Convenience methods
    def update_lap(self, current: int, total: int):
        """Update lap counter."""
        self.send_command("LAP", f"{current}/{total}")

    def update_position(self, position: int):
        """Update driver position."""
        self.send_command("POSITION", str(position))

    def update_gap(self, gap: float):
        """Update gap to car behind (positive) or ahead (negative)."""
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
        if self.ser:
            self.ser.close()

# Example usage
if __name__ == "__main__":
    display = DriverDisplay(port='/dev/ttyUSB0')

    # Simulate race sequence
    display.update_lap(10, 58)
    display.update_position(2)
    display.update_gap(1.2)
    display.set_tire_status("OK")
    time.sleep(3)

    # Pit strategy decided
    display.set_strategy("A")
    display.set_pit_countdown(5)
    time.sleep(2)

    # Countdown
    for i in range(5, 0, -1):
        display.set_pit_countdown(i)
        time.sleep(2)

    # Pit now
    display.pit_now()
    time.sleep(3)

    # Back to racing
    display.clear()
    display.update_lap(16, 58)

    display.close()
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-18
**Status:** Planning Phase
**Related Documents:** PRD_Full_System.md
