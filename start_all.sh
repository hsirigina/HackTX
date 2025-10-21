#!/bin/bash

# Start all servers together
echo "🚀 Starting HackTX F1 Strategy System..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start Driver Bridge (Arduino Display) in background
echo "📟 Starting Driver Bridge (Arduino Display)..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
# Run driver_bridge in background but with output visible
(python driver_bridge.py 2>&1 | sed 's/^/[DRIVER_BRIDGE] /') &
DRIVER_PID=$!

# Wait a moment for driver bridge to connect to Arduino
sleep 3

# Start backend API server in background
echo "🏎️  Starting API Server..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python api_server.py &
API_PID=$!

# Wait a moment for API server to start
sleep 2

# Start backend gesture server in background (suppress HTTP logs)
echo "🎥 Starting Gesture Recognition Server..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python gesture_server.py > /dev/null 2>&1 &
GESTURE_PID=$!

# Wait a moment for gesture server to start
sleep 2

# Start frontend
echo ""
echo "⚛️  Starting Frontend..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ All servers started!"
echo "📟 Driver Bridge: Connected to Arduino on /dev/tty.usbmodem*"
echo "🏎️  API Server: http://localhost:8000"
echo "📹 Gesture Server: http://localhost:5001"
echo "🌐 Frontend: http://localhost:5173 or http://localhost:5174"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping all servers...'; kill $DRIVER_PID $API_PID $GESTURE_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
