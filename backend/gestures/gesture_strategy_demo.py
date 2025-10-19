"""
Gesture-Controlled Strategy Dashboard Demo
Shows how gestures control race strategy selection
"""

import cv2
import time
import sys
import os
from typing import Optional, List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gestures.gesture_recognition import GestureRecognizer, GestureVisualizer


class StrategyScenario:
    """Represents a race strategy option"""
    def __init__(self, name: str, recommendation_type: str, tire_compound: str, 
                 pit_lap: int, reasoning: str, urgency: str, confidence: float):
        self.name = name
        self.recommendation_type = recommendation_type
        self.tire_compound = tire_compound
        self.pit_lap = pit_lap
        self.reasoning = reasoning
        self.urgency = urgency
        self.confidence = confidence


class GestureStrategyController:
    """Controls strategy browsing with gestures"""
    
    def __init__(self):
        # Sample strategy scenarios (would come from AI Coordinator in real system)
        self.scenarios = [
            StrategyScenario(
                name="Aggressive Undercut",
                recommendation_type="PIT_NOW",
                tire_compound="SOFT",
                pit_lap=65,
                reasoning="Pit now on SOFT tires. Piastri closing 0.3s/lap. Undercut opportunity before he pits. Push hard on outlap to gain track position.",
                urgency="HIGH",
                confidence=0.92
            ),
            StrategyScenario(
                name="Defensive Stay Out",
                recommendation_type="STAY_OUT",
                tire_compound="CURRENT (HARD)",
                pit_lap=70,
                reasoning="Stay out 5 more laps. Tires still have life. Force Piastri to pit first, then react. Track position critical at Monaco.",
                urgency="MEDIUM",
                confidence=0.85
            ),
            StrategyScenario(
                name="Conservative Medium",
                recommendation_type="PIT_SOON",
                tire_compound="MEDIUM",
                pit_lap=67,
                reasoning="Pit in 2 laps for MEDIUM compound. Balanced approach - fresher tires than staying out, more durable than SOFT. Safe points finish.",
                urgency="MEDIUM",
                confidence=0.88
            )
        ]
        
        self.current_index = 0
        self.locked_scenario = None
        self.show_details = False
        
        # Gesture recognizer
        self.recognizer = GestureRecognizer(confidence_threshold=0.80)
        
        # State
        self.last_action = "System Ready"
        self.last_action_time = time.time()
        
    def next_scenario(self):
        """Navigate to next scenario"""
        self.current_index = (self.current_index + 1) % len(self.scenarios)
        self.show_details = False
        self.last_action = f"→ Next: {self.scenarios[self.current_index].name}"
        self.last_action_time = time.time()
        print(f"\n▶️  SWIPE RIGHT → Next scenario: {self.scenarios[self.current_index].name}")
        
    def previous_scenario(self):
        """Navigate to previous scenario"""
        self.current_index = (self.current_index - 1) % len(self.scenarios)
        self.show_details = False
        self.last_action = f"← Previous: {self.scenarios[self.current_index].name}"
        self.last_action_time = time.time()
        print(f"\n◀️  SWIPE LEFT ← Previous scenario: {self.scenarios[self.current_index].name}")
        
    def lock_in_strategy(self):
        """Lock in current strategy"""
        scenario = self.scenarios[self.current_index]
        self.locked_scenario = scenario
        self.last_action = f"✅ LOCKED: {scenario.name}"
        self.last_action_time = time.time()
        print(f"\n👍 THUMBS UP → STRATEGY LOCKED!")
        print(f"   📋 Executing: {scenario.name}")
        print(f"   🏁 Action: {scenario.recommendation_type}")
        print(f"   🛞 Tires: {scenario.tire_compound}")
        print(f"   📍 Pit Lap: {scenario.pit_lap}")
        
    def toggle_details(self):
        """Toggle detailed view"""
        self.show_details = not self.show_details
        status = "SHOWING" if self.show_details else "HIDING"
        self.last_action = f"✌️ Details {status}"
        self.last_action_time = time.time()
        print(f"\n✌️  PEACE SIGN → Details {status}")
        
    def get_current_scenario(self) -> StrategyScenario:
        """Get currently selected scenario"""
        return self.scenarios[self.current_index]
    
    def draw_dashboard(self, frame):
        """Draw strategy dashboard overlay on frame"""
        height, width = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        
        # Get current scenario
        scenario = self.get_current_scenario()
        
        # Main panel - right side
        panel_x = width - 500
        panel_y = 50
        panel_width = 480
        panel_height = 600
        
        # Draw main panel background
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (40, 40, 40), -1)
        
        # Blend
        alpha = 0.85
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # === HEADER ===
        y = panel_y + 40
        cv2.putText(frame, "RACE STRATEGY", (panel_x + 20, y), 
                   cv2.FONT_HERSHEY_BOLD, 0.9, (255, 255, 255), 2)
        
        # Scenario counter
        counter_text = f"{self.current_index + 1}/{len(self.scenarios)}"
        cv2.putText(frame, counter_text, (panel_x + panel_width - 80, y), 
                   cv2.FONT_HERSHEY_BOLD, 0.7, (150, 150, 150), 2)
        
        y += 10
        cv2.line(frame, (panel_x + 20, y), (panel_x + panel_width - 20, y), 
                (100, 100, 100), 2)
        
        # === SCENARIO NAME ===
        y += 45
        # Color based on urgency
        urgency_colors = {
            "LOW": (100, 255, 100),
            "MEDIUM": (100, 200, 255),
            "HIGH": (100, 150, 255),
            "CRITICAL": (100, 100, 255)
        }
        name_color = urgency_colors.get(scenario.urgency, (255, 255, 255))
        cv2.putText(frame, scenario.name, (panel_x + 20, y), 
                   cv2.FONT_HERSHEY_BOLD, 0.8, name_color, 2)
        
        # === QUICK INFO ===
        y += 50
        info_items = [
            ("Action:", scenario.recommendation_type, (255, 200, 100)),
            ("Tires:", scenario.tire_compound, (150, 255, 150)),
            ("Pit Lap:", str(scenario.pit_lap), (150, 200, 255)),
            ("Urgency:", scenario.urgency, name_color),
            ("Confidence:", f"{scenario.confidence:.0%}", (200, 200, 200))
        ]
        
        for label, value, color in info_items:
            cv2.putText(frame, label, (panel_x + 30, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
            cv2.putText(frame, value, (panel_x + 140, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y += 30
        
        # === REASONING (Main or Detailed) ===
        y += 20
        cv2.line(frame, (panel_x + 20, y), (panel_x + panel_width - 20, y), 
                (100, 100, 100), 1)
        y += 30
        
        cv2.putText(frame, "Strategy Reasoning:", (panel_x + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 100), 1)
        y += 25
        
        # Word wrap reasoning text
        reasoning = scenario.reasoning
        max_width = 55
        words = reasoning.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_width:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        for line in lines[:5]:  # Max 5 lines
            cv2.putText(frame, line, (panel_x + 25, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
            y += 22
        
        # === DETAILED VIEW ===
        if self.show_details:
            y += 20
            cv2.rectangle(frame, (panel_x + 15, y), 
                         (panel_x + panel_width - 15, y + 100), 
                         (60, 60, 100), -1)
            y += 25
            cv2.putText(frame, "DETAILED BREAKDOWN:", (panel_x + 25, y), 
                       cv2.FONT_HERSHEY_BOLD, 0.5, (255, 255, 150), 1)
            y += 25
            
            details = [
                f"• Tire life: {scenario.pit_lap - 60} more laps",
                f"• Pace delta: 0.3s/lap disadvantage",
                f"• Track position: Critical",
                f"• Alternative: Extend 5 laps"
            ]
            
            for detail in details:
                cv2.putText(frame, detail, (panel_x + 30, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                y += 18
        
        # === LOCKED INDICATOR ===
        if self.locked_scenario:
            lock_y = panel_y + panel_height - 80
            cv2.rectangle(frame, (panel_x + 15, lock_y), 
                         (panel_x + panel_width - 15, lock_y + 60), 
                         (50, 150, 50), -1)
            cv2.putText(frame, "✓ STRATEGY LOCKED", (panel_x + 80, lock_y + 40), 
                       cv2.FONT_HERSHEY_BOLD, 0.8, (255, 255, 255), 2)
        
        # === LAST ACTION ===
        action_y = height - 30
        current_time = time.time()
        if current_time - self.last_action_time < 3.0:  # Show for 3 seconds
            cv2.rectangle(frame, (10, action_y - 35), (400, action_y + 5), 
                         (50, 50, 50), -1)
            cv2.putText(frame, self.last_action, (20, action_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
        
        return frame


def main():
    """Main demo function"""
    print("=" * 70)
    print("Gesture-Controlled Race Strategy Dashboard")
    print("=" * 70)
    print("\n📋 Scenario:")
    print("   Monaco 2024, Lap 65")
    print("   Charles Leclerc (LEC) - P1")
    print("   Oscar Piastri (PIA) - P2, 0.8s behind, closing fast\n")
    
    print("🎮 Gesture Controls:")
    print("   Swipe Right ➡️  - Next strategy scenario")
    print("   Swipe Left  ⬅️  - Previous strategy scenario")
    print("   Thumbs Up   👍 - Lock in selected strategy")
    print("   Peace Sign  ✌️  - Show/Hide detailed breakdown\n")
    
    print("Press 'q' to quit\n")
    print("=" * 70)
    
    # Initialize controller
    controller = GestureStrategyController()
    
    # Initialize webcam
    camera_index = 1  # Mac camera
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Camera {camera_index} not available, trying camera 0...")
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # FPS calculation
    fps_time = time.time()
    fps = 0
    
    print("✅ System ready! Perform gestures to control the dashboard.\n")
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process gestures
            annotated_frame, gesture_result = controller.recognizer.process_frame(frame)
            
            # Handle detected gestures
            if gesture_result:
                gesture_name = gesture_result.gesture_name
                
                if gesture_name == GestureRecognizer.SWIPE_RIGHT:
                    controller.next_scenario()
                
                elif gesture_name == GestureRecognizer.SWIPE_LEFT:
                    controller.previous_scenario()
                
                elif gesture_name == GestureRecognizer.THUMBS_UP:
                    controller.lock_in_strategy()
                
                elif gesture_name == GestureRecognizer.PEACE_SIGN:
                    controller.toggle_details()
            
            # Draw strategy dashboard
            annotated_frame = controller.draw_dashboard(annotated_frame)
            
            # Calculate FPS
            current_fps_time = time.time()
            fps = 1.0 / (current_fps_time - fps_time)
            fps_time = current_fps_time
            
            # Draw FPS
            cv2.putText(
                annotated_frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            
            # Display frame
            cv2.imshow('Gesture Strategy Dashboard', annotated_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        print("\n" + "=" * 70)
        print("Session Summary:")
        if controller.locked_scenario:
            print(f"✅ Locked Strategy: {controller.locked_scenario.name}")
            print(f"   Action: {controller.locked_scenario.recommendation_type}")
            print(f"   Tires: {controller.locked_scenario.tire_compound}")
        else:
            print("⚠️  No strategy locked in")
        print("=" * 70)
        
        controller.recognizer.cleanup()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

