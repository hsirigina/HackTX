"""
Simple gesture server that exposes gestures via HTTP
Frontend can poll this to get the latest gesture
"""

from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from gestures.gesture_recognition import GestureRecognizer

app = Flask(__name__)
CORS(app)

# Global state
latest_gesture = {
    'gesture': 'No Gesture',
    'confidence': 0,
    'timestamp': time.time()
}

gesture_lock = threading.Lock()

def run_gesture_recognition():
    """Run gesture recognition in background thread"""
    import cv2
    from gestures.gesture_recognition import GestureVisualizer
    
    recognizer = GestureRecognizer()
    
    print("🎥 Starting camera...")

    # Try camera index 0 first (built-in Mac camera), then 1 (might be iPhone)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera 0 not available, trying camera 1...")
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("❌ ERROR: Could not open camera!")
        return
    
    print("✅ Camera opened successfully!")
    print("👋 Wave your hand to test gestures")
    print("🎥 Running in headless mode (no window)")
    print("✋ Gestures will be detected and sent to frontend automatically")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process frame for gestures (no visualization needed)
        _, result = recognizer.process_frame(frame)
        
        # Update global gesture state
        if result:
            with gesture_lock:
                global latest_gesture
                latest_gesture = {
                    'gesture': result.gesture_name,
                    'confidence': result.confidence,
                    'timestamp': result.timestamp
                }
            print(f"✋ Detected: {result.gesture_name} ({result.confidence:.2f})")
        
        # Small delay to control frame rate
        cv2.waitKey(1)
    
    cap.release()
    recognizer.cleanup()

@app.route('/api/gesture', methods=['GET'])
def get_gesture():
    """Get the latest detected gesture"""
    with gesture_lock:
        # Clear gesture after 1 second to avoid repeats
        if time.time() - latest_gesture['timestamp'] > 1.0:
            return jsonify({
                'gesture': 'No Gesture',
                'confidence': 0,
                'timestamp': time.time()
            })
        
        return jsonify(latest_gesture)

@app.route('/api/gesture/clear', methods=['POST'])
def clear_gesture():
    """Clear the current gesture"""
    with gesture_lock:
        global latest_gesture
        latest_gesture = {
            'gesture': 'No Gesture',
            'confidence': 0,
            'timestamp': time.time()
        }
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    # Start gesture recognition in background
    gesture_thread = threading.Thread(target=run_gesture_recognition, daemon=True)
    gesture_thread.start()
    
    # Give camera time to initialize
    time.sleep(2)
    
    print("🚀 Gesture server starting on http://localhost:5001")
    print("📡 Frontend can poll /api/gesture for gestures")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

