"""
Gesture Recognition Demo
Run this to test the gesture recognition system with your webcam
"""

import cv2
import time
import sys
import os

# Add parent directory to path so we can import from gestures package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gestures.gesture_recognition import GestureRecognizer, GestureVisualizer


def main():
    """Main demo function"""
    print("=" * 60)
    print("Gesture Recognition Demo")
    print("=" * 60)
    print("\nSupported Gestures:")
    print("  1. Swipe Right - Move open hand left to right (Next scenario)")
    print("  2. Swipe Left - Move open hand right to left (Previous scenario)")
    print("  3. Thumbs Up - Lock in selected strategy")
    print("  4. Peace Sign - Show details")
    print("\nPress 'q' to quit")
    print("=" * 60)
    
    # Initialize webcam - try different camera indices
    # 0 is usually first camera (might be Continuity Camera)
    # 1 is usually built-in Mac camera
    camera_index = 1  # Change to 0 if you want iPhone, 1 for Mac camera
    
    cap = cv2.VideoCapture(camera_index)
    
    # If that fails, try other cameras
    if not cap.isOpened():
        print(f"Camera {camera_index} not available, trying camera 0...")
        cap = cv2.VideoCapture(0)
    
    # Set camera properties for 30 FPS
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Initialize gesture recognizer with slightly lower threshold for better motion detection
    recognizer = GestureRecognizer(confidence_threshold=0.80)
    
    # FPS calculation
    fps_time = time.time()
    fps = 0
    
    # Gesture history for logging
    gesture_count = {
        GestureRecognizer.SWIPE_RIGHT: 0,
        GestureRecognizer.SWIPE_LEFT: 0,
        GestureRecognizer.THUMBS_UP: 0,
        GestureRecognizer.PEACE_SIGN: 0
    }
    
    last_gesture_result = None
    gesture_display_time = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame
            annotated_frame, gesture_result = recognizer.process_frame(frame)
            
            # Update gesture result with display timeout
            current_time = time.time()
            if gesture_result:
                last_gesture_result = gesture_result
                gesture_display_time = current_time
                gesture_count[gesture_result.gesture_name] += 1
                
                # Log to console
                print(f"\n[{gesture_result.gesture_name}] detected "
                      f"(confidence: {gesture_result.confidence:.2%})")
            
            # Clear gesture display after 2 seconds
            if current_time - gesture_display_time > 2.0:
                last_gesture_result = None
            
            # Calculate FPS
            current_fps_time = time.time()
            fps = 1.0 / (current_fps_time - fps_time)
            fps_time = current_fps_time
            
            # Draw visualization
            annotated_frame = GestureVisualizer.draw_gesture_info(
                annotated_frame,
                last_gesture_result,
                fps
            )
            
            # Draw statistics
            y_pos = annotated_frame.shape[0] - 180
            cv2.putText(
                annotated_frame,
                "Detection Count:",
                (annotated_frame.shape[1] - 250, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            y_pos += 25
            
            for gesture_name, count in gesture_count.items():
                cv2.putText(
                    annotated_frame,
                    f"{gesture_name}: {count}",
                    (annotated_frame.shape[1] - 250, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )
                y_pos += 20
            
            # Display frame
            cv2.imshow('Gesture Recognition Demo', annotated_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        print("\n" + "=" * 60)
        print("Session Summary:")
        print("=" * 60)
        total_gestures = sum(gesture_count.values())
        print(f"Total gestures detected: {total_gestures}")
        for gesture_name, count in gesture_count.items():
            if count > 0:
                percentage = (count / total_gestures * 100) if total_gestures > 0 else 0
                print(f"  {gesture_name}: {count} ({percentage:.1f}%)")
        print("=" * 60)
        
        recognizer.cleanup()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

