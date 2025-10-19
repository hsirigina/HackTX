#!/bin/bash

# Start the gesture recognition server
cd "$(dirname "$0")"

echo "🎥 Starting Gesture Recognition Server..."
echo "📹 Camera will start in a moment"
echo "✋ Swipe left/right with your hand to control scenarios"
echo ""

source ../venv/bin/activate
python gesture_server.py

