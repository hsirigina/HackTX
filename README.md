# F1 Multi-Agent Race Strategy System

An AI-powered F1 race strategy system featuring specialized autonomous agents that analyze live race data, run simulations, debate strategies, and communicate recommendations to both pit crew engineers and drivers.

## Project Structure

```
.
├── backend/           # Python backend (agents, replay, API)
├── frontend/          # React dashboard
├── arduino/           # Arduino driver display code
├── data/              # Historical race data cache
├── PRD_Full_System.md # Complete system documentation
└── PRD_Arduino_Driver_Display.md # Arduino-specific docs
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration

Copy `.env.example` to `.env` and fill in:
- Supabase URL and API key
- Anthropic API key
- Arduino port (optional)

### Run the System

```bash
# Start backend
cd backend
python main.py

# Start frontend (separate terminal)
cd frontend
npm install
npm start

# Upload Arduino code
# Open arduino/driver_display/driver_display.ino in Arduino IDE and upload
```

## Documentation

- [Full System PRD](PRD_Full_System.md) - Complete architecture and specifications
- [Arduino PRD](PRD_Arduino_Driver_Display.md) - Hardware setup and protocols

## Tech Stack

- **Backend**: Python, FastF1, Anthropic Claude API, FastAPI
- **Frontend**: React, TypeScript, MediaPipe, Supabase JS
- **Database**: Supabase (PostgreSQL)
- **Hardware**: Arduino Nano, 16x2 LCD Display

## Demo

Uses historical F1 race data (via FastF1) replayed in real-time to simulate live race conditions. Perfect for hackathon demonstrations without waiting for an actual race.

---

Built for HackTX 2024