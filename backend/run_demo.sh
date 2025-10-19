#!/bin/bash
# Quick launcher for interactive race simulator

cd "$(dirname "$0")"

echo "🏎️  F1 Interactive Race Simulator"
echo "================================"
echo ""
echo "Choose mode:"
echo "1) Demo Mode (~5-8 decisions, 2-3 minutes)"
echo "2) Full Mode (~25 decisions, 10-15 minutes)"
echo ""
read -p "Enter choice (1 or 2): " choice

source venv/bin/activate

if [ "$choice" == "1" ]; then
    echo ""
    echo "Starting DEMO MODE..."
    python run_interactive_simulator.py --demo
else
    echo ""
    echo "Starting FULL MODE..."
    python run_interactive_simulator.py
fi
