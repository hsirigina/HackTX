"""
Gesture Recognition System using MediaPipe Hands
Detects: Fist Pump, Swipe Right, Swipe Left, Point, Open Palm
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import Optional, List, Tuple
import time


@dataclass
class GestureResult:
    """Result of gesture detection"""
    gesture_name: str
    confidence: float
    timestamp: float


class GestureRecognizer:
    """
    Recognizes hand gestures using MediaPipe Hands
    """
    
    # Gesture names
    FIST_PUMP = "Fist Pump"
    SWIPE_RIGHT = "Swipe Right"
    SWIPE_LEFT = "Swipe Left"
    POINT = "Point"
    OPEN_PALM = "Open Palm"
    NO_GESTURE = "No Gesture"
    
    def __init__(self, confidence_threshold=0.85, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize gesture recognizer
        
        Args:
            confidence_threshold: Minimum confidence for gesture detection (default: 0.85)
            detection_confidence: MediaPipe detection confidence
            tracking_confidence: MediaPipe tracking confidence
        """
        self.confidence_threshold = confidence_threshold
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # History for motion-based gestures
        self.position_history = deque(maxlen=15)  # ~0.5 seconds at 30 FPS
        self.height_history = deque(maxlen=10)
        
        # State tracking
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.8  # seconds - reduced for more responsive detection
        
    def _is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id, finger_mcp_id):
        """Check if a finger is extended"""
        tip = landmarks[finger_tip_id]
        pip = landmarks[finger_pip_id]
        mcp = landmarks[finger_mcp_id]
        
        # Finger is extended if tip is higher (lower y value) than pip and mcp
        return tip.y < pip.y and tip.y < mcp.y
    
    def _is_thumb_extended(self, landmarks):
        """Check if thumb is extended"""
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Thumb extends horizontally
        return abs(thumb_tip.x - thumb_mcp.x) > abs(thumb_ip.x - thumb_mcp.x)
    
    def _detect_fist(self, landmarks):
        """Detect if hand is in a fist"""
        # Check if all fingers are curled
        fingers_curled = 0
        
        # Index finger
        if not self._is_finger_extended(landmarks, 8, 6, 5):
            fingers_curled += 1
        
        # Middle finger
        if not self._is_finger_extended(landmarks, 12, 10, 9):
            fingers_curled += 1
            
        # Ring finger
        if not self._is_finger_extended(landmarks, 16, 14, 13):
            fingers_curled += 1
            
        # Pinky
        if not self._is_finger_extended(landmarks, 20, 18, 17):
            fingers_curled += 1
        
        return fingers_curled >= 3
    
    def _detect_open_palm(self, landmarks):
        """Detect open palm (all fingers extended)"""
        fingers_extended = 0
        
        # Thumb
        if self._is_thumb_extended(landmarks):
            fingers_extended += 1
        
        # Index finger
        if self._is_finger_extended(landmarks, 8, 6, 5):
            fingers_extended += 1
        
        # Middle finger
        if self._is_finger_extended(landmarks, 12, 10, 9):
            fingers_extended += 1
            
        # Ring finger
        if self._is_finger_extended(landmarks, 16, 14, 13):
            fingers_extended += 1
            
        # Pinky
        if self._is_finger_extended(landmarks, 20, 18, 17):
            fingers_extended += 1
        
        return fingers_extended >= 4
    
    def _detect_point(self, landmarks):
        """Detect pointing gesture (only index finger extended)"""
        # Index finger must be extended
        if not self._is_finger_extended(landmarks, 8, 6, 5):
            return False
        
        # Other fingers should be curled
        middle_curled = not self._is_finger_extended(landmarks, 12, 10, 9)
        ring_curled = not self._is_finger_extended(landmarks, 16, 14, 13)
        pinky_curled = not self._is_finger_extended(landmarks, 20, 18, 17)
        
        return middle_curled and ring_curled and pinky_curled
    
    def _detect_swipe(self):
        """Detect horizontal swipe gestures"""
        if len(self.position_history) < 8:  # Reduced from 10 for faster detection
            return None, 0.0
        
        # Get positions
        positions = list(self.position_history)
        start_x = positions[0][0]
        end_x = positions[-1][0]
        
        # Calculate horizontal movement
        dx = end_x - start_x
        
        # Lowered threshold for easier detection
        movement_threshold = 0.10  # Reduced from 0.15 (10% of frame)
        
        if abs(dx) > movement_threshold:
            # Check if movement is generally consistent (allow some jitter)
            # Count how many movements are in the right direction
            direction_count = 0
            total_moves = len(positions) - 1
            
            if dx > 0:  # Moving right
                for i in range(total_moves):
                    if positions[i+1][0] >= positions[i][0] - 0.02:  # Allow small backward jitter
                        direction_count += 1
                
                # Need at least 70% of movements in right direction
                if direction_count / total_moves >= 0.7:
                    confidence = min(abs(dx) / 0.25, 1.0)  # Adjusted confidence scale
                    return self.SWIPE_RIGHT, confidence
            
            else:  # Moving left
                for i in range(total_moves):
                    if positions[i+1][0] <= positions[i][0] + 0.02:  # Allow small forward jitter
                        direction_count += 1
                
                # Need at least 70% of movements in left direction
                if direction_count / total_moves >= 0.7:
                    confidence = min(abs(dx) / 0.25, 1.0)  # Adjusted confidence scale
                    return self.SWIPE_LEFT, confidence
        
        return None, 0.0
    
    def _detect_fist_pump(self):
        """Detect fist pump (fist raised quickly)"""
        if len(self.height_history) < 6:  # Reduced from 8 for faster detection
            return False, 0.0
        
        heights = list(self.height_history)
        
        # Check if hand moved up
        start_y = heights[0]
        end_y = heights[-1]
        
        # Y decreases as hand moves up in image coordinates
        dy = start_y - end_y
        
        # Lowered threshold for easier detection
        if dy > 0.10:  # Reduced from 0.15 (10% of frame)
            # Check if movement is generally upward (allow some jitter)
            upward_count = 0
            total_moves = len(heights) - 1
            
            for i in range(total_moves):
                if heights[i] >= heights[i+1] - 0.02:  # Allow small downward jitter
                    upward_count += 1
            
            # Need at least 65% of movements upward (more lenient than swipes)
            if upward_count / total_moves >= 0.65:
                confidence = min(dy / 0.20, 1.0)  # Adjusted confidence scale
                return True, confidence
        
        return False, 0.0
    
    def process_frame(self, frame) -> Tuple[np.ndarray, Optional[GestureResult]]:
        """
        Process a single frame and detect gestures
        
        Args:
            frame: BGR image from camera
            
        Returns:
            Tuple of (annotated_frame, gesture_result)
        """
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        gesture_result = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Get landmarks
                landmarks = hand_landmarks.landmark
                
                # Get wrist position for tracking
                wrist = landmarks[0]
                self.position_history.append((wrist.x, wrist.y))
                self.height_history.append(wrist.y)
                
                # Detect static gestures first
                current_time = time.time()
                
                # Check cooldown
                if current_time - self.last_gesture_time < self.gesture_cooldown:
                    continue
                
                detected_gesture = None
                confidence = 0.0
                
                # Check for fist (for fist pump detection)
                is_fist = self._detect_fist(landmarks)
                
                if is_fist:
                    # Check for fist pump (upward motion)
                    is_pump, pump_confidence = self._detect_fist_pump()
                    if is_pump and pump_confidence >= self.confidence_threshold:
                        detected_gesture = self.FIST_PUMP
                        confidence = pump_confidence
                
                # Check for swipes
                if not detected_gesture:
                    swipe_gesture, swipe_confidence = self._detect_swipe()
                    if swipe_gesture and swipe_confidence >= self.confidence_threshold:
                        detected_gesture = swipe_gesture
                        confidence = swipe_confidence
                
                # Check for point
                if not detected_gesture and self._detect_point(landmarks):
                    detected_gesture = self.POINT
                    confidence = 0.95
                
                # Check for open palm
                if not detected_gesture and self._detect_open_palm(landmarks):
                    detected_gesture = self.OPEN_PALM
                    confidence = 0.95
                
                # Create result if gesture detected
                if detected_gesture and confidence >= self.confidence_threshold:
                    gesture_result = GestureResult(
                        gesture_name=detected_gesture,
                        confidence=confidence,
                        timestamp=current_time
                    )
                    self.last_gesture = detected_gesture
                    self.last_gesture_time = current_time
                    
                    # Clear history after motion gesture
                    if detected_gesture in [self.SWIPE_LEFT, self.SWIPE_RIGHT, self.FIST_PUMP]:
                        self.position_history.clear()
                        self.height_history.clear()
        
        return frame, gesture_result
    
    def cleanup(self):
        """Release resources"""
        self.hands.close()


class GestureVisualizer:
    """Helper class for visualizing gesture detection"""
    
    @staticmethod
    def draw_gesture_info(frame, gesture_result: Optional[GestureResult], fps: float = 0.0):
        """
        Draw gesture information on frame
        
        Args:
            frame: Image frame to draw on
            gesture_result: Detected gesture result
            fps: Current FPS
        """
        height, width = frame.shape[:2]
        
        # Draw FPS
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Draw gesture result
        if gesture_result:
            text = f"{gesture_result.gesture_name}"
            confidence_text = f"Confidence: {gesture_result.confidence:.2%}"
            
            # Background rectangle
            cv2.rectangle(
                frame,
                (10, height - 100),
                (400, height - 20),
                (0, 255, 0),
                -1
            )
            
            # Text
            cv2.putText(
                frame,
                text,
                (20, height - 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 0),
                2
            )
            cv2.putText(
                frame,
                confidence_text,
                (20, height - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2
            )
        else:
            # Show instruction
            cv2.putText(
                frame,
                "Perform a gesture...",
                (10, height - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
        
        # Draw gesture guide
        y_pos = 60
        gestures_guide = [
            "Gestures:",
            "- Fist Pump: Closed fist, raise up quickly",
            "- Swipe Right: Move hand right",
            "- Swipe Left: Move hand left",
            "- Point: Index finger extended",
            "- Open Palm: All fingers extended"
        ]
        
        for text in gestures_guide:
            cv2.putText(
                frame,
                text,
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            y_pos += 25
        
        return frame

