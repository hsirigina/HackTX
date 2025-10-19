"""
Integration: Gesture System → Arduino Display
When you lock in a strategy with thumbs up, send it to the driver's Arduino
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arduino_controller import ArduinoController
import cv2
import time
from gestures.gesture_recognition import GestureRecognizer, GestureVisualizer


class GestureArduinoIntegration:
    """Connects gesture controls to Arduino display"""
    
    def __init__(self, race_id: str = 'monaco_2024'):
        self.arduino = ArduinoController(race_id=race_id)
        self.recognizer = GestureRecognizer(confidence_threshold=0.80)
        
        # Simulated race state
        self.current_lap = 65
        self.total_laps = 78
        self.position = 'P1'
        self.gap = '+2.3'
        
        # Strategy scenarios
        self.scenarios = [
            {
                'name': 'Aggressive Undercut',
                'pit_lap': 65,
                'compound': 'SOFT',
                'countdown': 0
            },
            {
                'name': 'Defensive Stay Out',
                'pit_lap': 70,
                'compound': 'HARD',
                'countdown': 5
            },
            {
                'name': 'Conservative Medium',
                'pit_lap': 67,
                'compound': 'MEDIUM',
                'countdown': 2
            }
        ]
        
        self.current_scenario_index = 0
        self.locked_scenario = None
    
    def get_current_scenario(self):
        return self.scenarios[self.current_scenario_index]
    
    def next_scenario(self):
        self.current_scenario_index = (self.current_scenario_index + 1) % len(self.scenarios)
        scenario = self.get_current_scenario()
        print(f"\n→ Next scenario: {scenario['name']}")
    
    def previous_scenario(self):
        self.current_scenario_index = (self.current_scenario_index - 1) % len(self.scenarios)
        scenario = self.get_current_scenario()
        print(f"\n← Previous scenario: {scenario['name']}")
    
    def lock_in_strategy(self):
        """When thumbs up detected - send to Arduino!"""
        scenario = self.get_current_scenario()
        self.locked_scenario = scenario
        
        print(f"\n👍 THUMBS UP → STRATEGY LOCKED!")
        print(f"   Strategy: {scenario['name']}")
        print(f"   Pit Lap: {scenario['pit_lap']}")
        print(f"   Compound: {scenario['compound']}")
        
        countdown = scenario['pit_lap'] - self.current_lap
        
        if countdown <= 0:
            # Pit NOW
            print(f"   🔥 SENDING TO ARDUINO: PIT NOW (will buzz)")
            self.arduino.send_pit_now(
                lap=scenario['pit_lap'],
                compound=scenario['compound']
            )
        else:
            # Pit countdown
            print(f"   ⏱️  SENDING TO ARDUINO: Pit in {countdown} laps")
            self.arduino.send_pit_countdown(countdown)
        
        return scenario
    
    def show_details(self):
        """Peace sign - just print details (Arduino stays same)"""
        scenario = self.get_current_scenario()
        print(f"\n✌️ PEACE SIGN → Showing details:")
        print(f"   Name: {scenario['name']}")
        print(f"   Pit Lap: {scenario['pit_lap']}")
        print(f"   Compound: {scenario['compound']}")
        print(f"   Countdown: {scenario['countdown']} laps")
    
    def run(self):
        """Run the integrated demo"""
        print("=" * 70)
        print("GESTURE → ARDUINO INTEGRATION DEMO")
        print("=" * 70)
        print("\nGestures:")
        print("  Swipe Right → - Next strategy")
        print("  Swipe Left  ← - Previous strategy")
        print("  Thumbs Up   👍 - Lock in & SEND TO ARDUINO")
        print("  Peace Sign  ✌️  - Show details")
        print("\nPress 'q' to quit\n")
        print("=" * 70)
        
        # Send initial lap update to Arduino
        print("\n📡 Sending initial lap update to Arduino...")
        self.arduino.send_lap_update(
            self.current_lap, self.total_laps, self.position, self.gap
        )
        
        # Initialize webcam
        cap = cv2.VideoCapture(1)  # Mac camera
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return
        
        cap.set(cv2.CAP_PROP_FPS, 30)
        fps_time = time.time()
        
        print("✅ System ready! Perform gestures...\n")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                annotated_frame, gesture_result = self.recognizer.process_frame(frame)
                
                # Handle gestures
                if gesture_result:
                    gesture_name = gesture_result.gesture_name
                    
                    if gesture_name == GestureRecognizer.SWIPE_RIGHT:
                        self.next_scenario()
                    
                    elif gesture_name == GestureRecognizer.SWIPE_LEFT:
                        self.previous_scenario()
                    
                    elif gesture_name == GestureRecognizer.THUMBS_UP:
                        self.lock_in_strategy()
                    
                    elif gesture_name == GestureRecognizer.PEACE_SIGN:
                        self.show_details()
                
                # Draw current scenario info
                scenario = self.get_current_scenario()
                y = 30
                cv2.putText(annotated_frame, f"Scenario: {scenario['name']}", 
                           (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y += 30
                cv2.putText(annotated_frame, f"Pit Lap: {scenario['pit_lap']} ({scenario['compound']})", 
                           (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if self.locked_scenario:
                    y += 30
                    cv2.putText(annotated_frame, "✓ SENT TO ARDUINO", 
                               (10, y), cv2.FONT_HERSHEY_BOLD, 0.7, (0, 255, 0), 2)
                
                # FPS
                current_time = time.time()
                fps = 1.0 / (current_time - fps_time)
                fps_time = current_time
                cv2.putText(annotated_frame, f"FPS: {fps:.1f}", 
                           (annotated_frame.shape[1] - 120, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.imshow('Gesture → Arduino Integration', annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\n\nInterrupted")
        
        finally:
            print("\n" + "=" * 70)
            if self.locked_scenario:
                print(f"✅ Locked Strategy: {self.locked_scenario['name']}")
                print(f"   Sent to Arduino display!")
            print("=" * 70)
            
            self.recognizer.cleanup()
            cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    integration = GestureArduinoIntegration(race_id='monaco_2024_demo')
    integration.run()

