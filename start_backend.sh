#!/bin/bash
cd /Users/vanishaswabhanam/Documents/GitHub/HackTX

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if packages are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install --quiet fastapi uvicorn google-generativeai websockets python-dotenv fastf1 supabase
fi

# Start backend
echo "🚀 Starting backend server..."
cd backend
python api_server.py

