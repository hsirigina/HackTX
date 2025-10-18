"""
Quick test to verify gesture recognition dependencies are installed correctly
"""

import sys
import os

# Add parent directory to path so we can import from gestures package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing gesture recognition dependencies...\n")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        print(f"  Version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✓ MediaPipe imported successfully")
        print(f"  Version: {mp.__version__}")
    except ImportError as e:
        print(f"✗ MediaPipe import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
        print(f"  Version: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        from gestures.gesture_recognition import GestureRecognizer, GestureVisualizer
        print("✓ Gesture recognition module imported successfully")
    except ImportError as e:
        print(f"✗ Gesture recognition module import failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("All dependencies installed correctly!")
    print("Run 'python gestures/gesture_demo.py' to test with webcam")
    print("="*60)
    return True


def test_webcam():
    """Test if webcam is accessible"""
    print("\nTesting webcam access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Could not open webcam")
            print("  Make sure no other application is using it")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("✗ Could not read frame from webcam")
            cap.release()
            return False
        
        print(f"✓ Webcam accessible")
        print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        
        cap.release()
        return True
    
    except Exception as e:
        print(f"✗ Webcam test failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    success = test_imports()
    
    if success:
        print("\nWould you like to test webcam access? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response == 'y':
                test_webcam()
        except:
            print("\nSkipping webcam test")
    else:
        print("\n❌ Setup incomplete. Install dependencies with:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

