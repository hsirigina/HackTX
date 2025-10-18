/*
 * F1 Driver Display System
 * Shows pit strategy information on LCD/OLED display
 *
 * Hardware:
 * - Arduino Nano/Uno
 * - 16x2 LCD with I2C module OR 128x64 OLED
 * - Serial connection to backend (USB)
 *
 * Serial Protocol:
 * Commands: COMMAND:VALUE\n
 * Example: PIT_COUNTDOWN:3\n
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD Configuration (adjust address if needed: 0x27 or 0x3F)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Display States
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

// Race data
int currentLap = 0;
int totalLaps = 78;
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

  // Initialize LCD
  lcd.init();
  lcd.backlight();

  // Startup message
  lcd.setCursor(0, 0);
  lcd.print("F1 DRIVER ALERT");
  lcd.setCursor(0, 1);
  lcd.print("SYSTEM READY");
  delay(2000);
  lcd.clear();

  Serial.println("Driver Display Ready");
}

void loop() {
  // Read serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  // Update display based on state
  updateDisplay();

  // Handle flashing animation
  if (currentState == STATE_PIT_IMMINENT || currentState == STATE_PIT_NOW) {
    unsigned long now = millis();
    if (now - lastFlashTime > flashInterval) {
      flashState = !flashState;
      lastFlashTime = now;
    }
  }

  delay(50);  // 20Hz update rate
}

void processCommand(String cmd) {
  cmd.trim();

  int separatorIndex = cmd.indexOf(':');
  if (separatorIndex == -1) return;  // Invalid format

  String command = cmd.substring(0, separatorIndex);
  String value = cmd.substring(separatorIndex + 1);

  // Debug output
  Serial.print("CMD: ");
  Serial.print(command);
  Serial.print(" = ");
  Serial.println(value);

  if (command == "LAP") {
    // Format: LAP:15/78
    int slashIndex = value.indexOf('/');
    if (slashIndex != -1) {
      currentLap = value.substring(0, slashIndex).toInt();
      totalLaps = value.substring(slashIndex + 1).toInt();
    }
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
    } else {
      currentState = STATE_MONITORING;
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

    case STATE_STRATEGY_UPDATE:
      lcd.setCursor(0, 0);
      lcd.print("STRATEGY UPDATE");
      lcd.setCursor(0, 1);
      lcd.print("NEW: ");
      lcd.print(strategy);
      break;

    case STATE_ANALYZING:
      lcd.setCursor(0, 0);
      lcd.print("TEAM ANALYZING..");
      lcd.setCursor(0, 1);
      lcd.print("STAND BY");
      break;
  }
}
