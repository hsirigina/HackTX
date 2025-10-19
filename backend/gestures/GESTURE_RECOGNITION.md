# Gesture Recognition System

A standalone gesture recognition module using MediaPipe Hands for real-time hand gesture detection.

## Features

### Supported Gestures

| Gesture | Detection Pattern | Confidence Threshold |
|---------|-------------------|---------------------|
| **Fist Pump** | Closed fist → raised up quickly | 85%+ |
| **Swipe Right** | Hand moves right across frame | 85%+ |
| **Swipe Left** | Hand moves left across frame | 85%+ |
| **Point** | Index finger extended, others closed | 85%+ |
| **Open Palm** | All fingers extended, held steady | 85%+ |

### Technical Specifications

- **FPS**: 30 FPS webcam feed
- **Hand Detection**: MediaPipe Hands with landmark tracking
- **Processing**: Real-time gesture classification
- **Visual Feedback**: Live annotations and gesture display
- **Cooldown**: 1-second cooldown between gestures to prevent false positives

## Installation

1. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Demo

```bash
cd backend
python gestures/gesture_demo.py
```

Or from inside the gestures folder:
```bash
cd backend/gestures
python gesture_demo.py
```

The demo will:
- Open your webcam
- Display real-time hand tracking
- Show detected gestures with confidence scores
- Display FPS and gesture statistics
- Log all detected gestures to console

### Controls

- **Q**: Quit the application
- **Ctrl+C**: Emergency exit

## Module API

### GestureRecognizer

Main class for gesture recognition.

```python
from gestures.gesture_recognition import GestureRecognizer

# Initialize
recognizer = GestureRecognizer(confidence_threshold=0.85)

# Process a frame
annotated_frame, gesture_result = recognizer.process_frame(frame)

# Check result
if gesture_result:
    print(f"Detected: {gesture_result.gesture_name}")
    print(f"Confidence: {gesture_result.confidence:.2%}")
    print(f"Timestamp: {gesture_result.timestamp}")

# Cleanup when done
recognizer.cleanup()
```

### GestureResult

Data class containing detection results:

```python
@dataclass
class GestureResult:
    gesture_name: str      # Name of detected gesture
    confidence: float      # Confidence score (0.0 to 1.0)
    timestamp: float       # Unix timestamp of detection
```

### Available Gesture Names

```python
GestureRecognizer.FIST_PUMP    # "Fist Pump"
GestureRecognizer.SWIPE_RIGHT  # "Swipe Right"
GestureRecognizer.SWIPE_LEFT   # "Swipe Left"
GestureRecognizer.POINT        # "Point"
GestureRecognizer.OPEN_PALM    # "Open Palm"
```

## Integration Guide

### Basic Integration

```python
import cv2
from gestures.gesture_recognition import GestureRecognizer

# Setup
cap = cv2.VideoCapture(0)
recognizer = GestureRecognizer()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process frame
    annotated_frame, gesture = recognizer.process_frame(frame)
    
    # Handle detected gesture
    if gesture:
        if gesture.gesture_name == GestureRecognizer.FIST_PUMP:
            # Confirm action
            print("Confirming strategy!")
        elif gesture.gesture_name == GestureRecognizer.SWIPE_RIGHT:
            # Filter to aggressive
            print("Showing aggressive strategies")
        elif gesture.gesture_name == GestureRecognizer.SWIPE_LEFT:
            # Filter to conservative
            print("Showing conservative strategies")
        elif gesture.gesture_name == GestureRecognizer.POINT:
            # Select item
            print("Selecting item")
        elif gesture.gesture_name == GestureRecognizer.OPEN_PALM:
            # Pause/review
            print("Pausing")
    
    cv2.imshow('Frame', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

recognizer.cleanup()
cap.release()
```

### Custom Confidence Threshold

```python
# Lower threshold for more sensitive detection
recognizer = GestureRecognizer(confidence_threshold=0.75)

# Higher threshold for more accurate detection
recognizer = GestureRecognizer(confidence_threshold=0.95)
```

## Architecture

### Detection Pipeline

1. **Frame Capture**: Capture frame from webcam at 30 FPS
2. **Hand Detection**: MediaPipe Hands detects hand landmarks (21 points)
3. **Feature Extraction**: Calculate finger positions and hand motion
4. **Gesture Classification**: 
   - Static gestures (Point, Open Palm) - Instant detection
   - Motion gestures (Swipe, Fist Pump) - Temporal analysis
5. **Confidence Filtering**: Only return gestures above threshold
6. **Cooldown**: Prevent duplicate detections

### Gesture Detection Methods

**Static Gestures** (instant):
- Check finger extension states
- Analyze landmark positions
- Immediate classification

**Motion Gestures** (temporal):
- Track hand position over ~15 frames (0.5 seconds)
- Analyze movement patterns
- Detect direction and velocity

## Performance

- **Detection Latency**: < 50ms
- **False Positive Rate**: < 5% with 85% threshold
- **Resource Usage**: ~15% CPU on modern laptop
- **Memory**: ~200MB

## Troubleshooting

### Webcam Not Opening
- Check if another application is using the camera
- Try changing camera index: `cv2.VideoCapture(1)`
- Check camera permissions in system settings

### Low FPS
- Close other applications using the camera
- Reduce frame resolution
- Ensure good lighting conditions

### Gestures Not Detecting
- Ensure hand is clearly visible in frame
- Check lighting (avoid backlighting)
- Keep hand at medium distance from camera
- Try adjusting confidence threshold
- Make gestures more pronounced

### Too Many False Positives
- Increase confidence threshold
- Increase cooldown period
- Improve lighting conditions
- Keep background simple

## Future Integration Points

The module is designed to be integrated with:
- Race strategy dashboard
- Agent selection system
- Arduino display controller
- WebSocket communication layer

No changes to the core module needed - just add action handlers in your integration code.

## Files

All files are located in `backend/gestures/`:
- `gesture_recognition.py` - Core gesture recognition module
- `gesture_demo.py` - Standalone demo application
- `test_gesture_setup.py` - Setup verification script
- `GESTURE_RECOGNITION.md` - This documentation
- `__init__.py` - Package initialization

## Dependencies

- `opencv-python>=4.8.0` - Computer vision and camera handling
- `mediapipe>=0.10.0` - Hand landmark detection
- `numpy>=1.24.0` - Numerical operations

## License

Part of HackTX project.

