/*
 * Driver Display System - Arduino Nano 33 BLE + Display + Buzzer + Touch Sensor
 * 
 * Hardware:
 * - Arduino Nano 33 BLE with TinyML Shield
 * - OLED Display 0.96" (I2C on SDA/SCL - 0x3C)
 * - Buzzer on D12
 * - Touch Sensor on D11
 * - USB connection to laptop running Python bridge
 * 
 * Function:
 * - Receives race info and alerts from Python bridge
 * - Displays messages on OLED screen
 * - Buzzes ONLY for pit stops
 * - Touch sensor for engineer alerts
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Display setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pin definitions
const int BUZZER_PIN = 12;  // D12
const int TOUCH_PIN = 11;   // D11

// Display state
String line1 = "F1 DRIVER";
String line2 = "READY";
String line3 = "";
String line4 = "";

bool shouldBuzz = false;
int displayMode = 0;  // 0=message, 1=engineer alert, 2=pit now

// Touch sensor state
bool lastTouchState = LOW;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 300;

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TOUCH_PIN, INPUT);
  
  // Initialize display
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("OLED initialization failed!");
    while (1);
  }
  
  Serial.println("OLED initialized successfully!");
  
  // Force clear display first
  display.clearDisplay();
  display.display();
  delay(100);
  
  // Startup screen
  displayStartup();
  delay(2000);
  
  Serial.println("DRIVER_DISPLAY_READY");
}

void loop() {
  // Check touch sensor
  checkTouchSensor();
  
  // Read commands from Python bridge
  if (Serial.available()) {
    Serial.println("DEBUG: Serial data available!");
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    Serial.print("DEBUG: Got command: ");
    Serial.println(cmd);
    processCommand(cmd);
  }
  
  // Update display (only every 100ms to avoid flickering)
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate > 100) {
    updateDisplay();
    lastDisplayUpdate = millis();
  }
  
  // Handle buzzer
  if (shouldBuzz) {
    buzzPitStop();
    shouldBuzz = false;
  }
  
  delay(10);
}

void checkTouchSensor() {
  bool touchState = digitalRead(TOUCH_PIN);
  
  if (touchState == HIGH && lastTouchState == LOW) {
    if (millis() - lastDebounceTime > debounceDelay) {
      // Touch detected!
      Serial.println("TOUCH:ENGINEER_ALERT");
      
      // Show engineer alert on display
      displayMode = 1;
      line1 = "*** ENGINEER ***";
      line2 = "*** ALERT! ***";
      line3 = "";
      line4 = "Check Radio";
      
      // Quick beep
      tone(BUZZER_PIN, 2000, 150);
      delay(200);
      tone(BUZZER_PIN, 2000, 150);
      
      lastDebounceTime = millis();
    }
  }
  
  lastTouchState = touchState;
}

void processCommand(String cmd) {
  Serial.print("Received: ");
  Serial.println(cmd);
  
  if (cmd.startsWith("MSG:")) {
    // Regular message - support multi-line with | separator
    String msg = cmd.substring(4);
    displayMode = 0;

    // Check if message contains | for multi-line
    int pipeIndex = msg.indexOf('|');
    if (pipeIndex != -1) {
      // Multi-line message
      line1 = msg.substring(0, pipeIndex);
      line2 = msg.substring(pipeIndex + 1);
      line3 = "";
      line4 = "";
    } else {
      // Single line message
      line1 = msg;
      line2 = "";
      line3 = "";
      line4 = "";
    }
  }
  else if (cmd == "BUZZ:PIT") {
    // Pit stop buzzer
    shouldBuzz = true;
  }
  else if (cmd == "ENGINEER_ALERT") {
    // Engineer touched sensor (from Python)
    displayMode = 1;
    line1 = "*** ENGINEER ***";
    line2 = "*** ALERT! ***";
    line3 = "";
    line4 = "Check Radio";
    
    tone(BUZZER_PIN, 2000, 150);
    delay(200);
    tone(BUZZER_PIN, 2000, 150);
  }
  else if (cmd.startsWith("LAP:")) {
    // Lap update - format: LAP:65/78:P1:+2.3
    displayMode = 0;
    line1 = cmd.substring(4);
    line2 = "TIRES OK";
    line3 = "";
    line4 = "";
  }
  else if (cmd.startsWith("PIT_COUNTDOWN:")) {
    // Pit countdown - format: PIT_COUNTDOWN:3
    int laps = cmd.substring(14).toInt();
    displayMode = 0;
    line1 = "LAPS TO PIT: " + String(laps);
    line2 = "";
    line3 = "STRATEGY A";
    line4 = "Stay focused!";
  }
  else if (cmd == "PIT_NOW") {
    // Urgent pit stop
    displayMode = 2;
    line1 = ">>> PIT NOW <<<";
    line2 = "";
    line3 = "BOX BOX BOX";
    line4 = "";
    shouldBuzz = true;
  }
  else if (cmd == "CLEAR") {
    // Clear to monitoring
    displayMode = 0;
    line1 = "LAP 65/78  P1";
    line2 = "TIRES OK";
    line3 = "GAP: +2.3s";
    line4 = "";
  }
}

void displayStartup() {
  Serial.println("Drawing startup screen...");
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 10);
  display.println("F1");
  display.setCursor(10, 30);
  display.println("DRIVER");
  display.setTextSize(1);
  display.setCursor(20, 50);
  display.println("READY");
  display.display();
  Serial.println("Startup screen drawn!");
}

void updateDisplay() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  if (displayMode == 1) {
    // Engineer alert - slow flash (1 second on/off)
    if ((millis() / 1000) % 2 == 0) {
      display.setTextSize(1);
      display.setCursor(5, 10);
      display.println(line1);
      display.setCursor(5, 25);
      display.println(line2);
      display.setCursor(5, 50);
      display.println(line4);
    }
  }
  else if (displayMode == 2) {
    // Pit now - medium flash (500ms on/off)
    if ((millis() / 500) % 2 == 0) {
      display.setTextSize(1);
      display.setCursor(0, 20);
      display.println(line1);
      display.setCursor(5, 40);
      display.println(line3);
    }
  }
  else {
    // Normal display - NO FLASHING
    // If showing default "F1 DRIVER READY", show it BIG
    if (line1 == "F1 DRIVER" && line2 == "READY") {
      display.setTextSize(2);
      display.setCursor(10, 10);
      display.println("F1");
      display.setCursor(10, 30);
      display.println("DRIVER");
      display.setTextSize(1);
      display.setCursor(20, 50);
      display.println("READY");
    } else {
      // Regular messages - small text
      display.setTextSize(1);
      display.setCursor(0, 5);
      display.println(line1);
      display.setCursor(0, 20);
      display.println(line2);
      display.setCursor(0, 35);
      display.println(line3);
      display.setCursor(0, 50);
      display.println(line4);
    }
  }
  
  display.display();
}

void buzzPitStop() {
  // Distinctive pit stop buzzer pattern
  tone(BUZZER_PIN, 1000, 300);
  delay(350);
  tone(BUZZER_PIN, 1000, 300);
  delay(350);
  tone(BUZZER_PIN, 1500, 500);
}
