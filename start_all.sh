#!/bin/bash

# Start all servers together
echo "🚀 Starting HackTX F1 Strategy System..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend API server in background
echo "🏎️  Starting API Server..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python api_server.py &
API_PID=$!

# Wait a moment for API server to start
sleep 2

# Start backend gesture server in background
echo "🎥 Starting Gesture Recognition Server..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python gesture_server.py &
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
echo "🏎️  API Server: http://localhost:8000"
echo "📹 Gesture Server: http://localhost:5001"
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping all servers...'; kill $API_PID $GESTURE_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
