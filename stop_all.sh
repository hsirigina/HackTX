#!/bin/bash

echo "🛑 Stopping all HackTX F1 services..."

# Kill all Python services
pkill -9 -f driver_bridge
pkill -9 -f api_server
pkill -9 -f gesture_server

# Kill frontend
lsof -ti :5173 | xargs kill -9 2>/dev/null
lsof -ti :5174 | xargs kill -9 2>/dev/null

# Kill backend ports
lsof -ti :8000 | xargs kill -9 2>/dev/null
lsof -ti :5001 | xargs kill -9 2>/dev/null

sleep 1

echo "✅ All services stopped"
echo ""
echo "Running processes check:"
ps aux | grep -E "(driver_bridge|api_server|gesture_server)" | grep python | grep -v grep || echo "  No Python services running ✓"
