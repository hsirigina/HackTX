# AI Toggle Feature

## Purpose

Allows you to test the system without making real AI API calls, useful for:
- Frontend integration testing
- Database/replay testing
- Saving API quota during development

## How to Use

### Disable AI (Mock Mode)

Edit `.env`:
```bash
DISABLE_AI=true
```

The system will:
- ✅ Run all 4 data agents normally (free)
- ✅ Detect events and triggers
- ✅ Return **mock recommendations** instead of calling Gemini API
- ✅ Save mock recommendations to Supabase
- ✅ Display mock data in frontend
- ❌ **NO API calls to Gemini**

### Enable AI (Production Mode)

Edit `.env`:
```bash
DISABLE_AI=false
```

Or remove the line entirely (defaults to false).

The system will:
- ✅ Run all 4 data agents
- ✅ Call Gemini API when events trigger
- ✅ Return real AI recommendations
- ⚠️ **Uses API quota**

## Mock Recommendation Format

When AI is disabled, the coordinator returns realistic mock data:

```json
{
  "consensus": "CLEAR",
  "recommendation_type": "PIT_SOON" | "STAY_OUT",
  "pit_window": [65, 67],
  "target_compound": "MEDIUM",
  "driver_instruction": "[MOCK] Continue pushing, 64 laps on HARD. Data agents monitoring.",
  "pit_crew_instruction": "[MOCK] Standby for potential pit stop. Monitor tire degradation.",
  "reasoning": "[MOCK DATA] AI is disabled. This is mock recommendation based on 2 detected events...",
  "urgency": "CRITICAL" | "HIGH" | "MEDIUM",
  "confidence": 0.85,
  "key_events": ["Old tires (64 laps on HARD)", "Close racing..."]
}
```

**Note:** All mock messages include `[MOCK]` or `[MOCK DATA]` prefix for easy identification.

## Mock Logic

The mock recommendation is based on detected events:

| Condition | Recommendation | Urgency | Confidence |
|-----------|----------------|---------|------------|
| CRITICAL events detected | PIT_SOON | CRITICAL | 85% |
| HIGH events detected | STAY_OUT | HIGH | 75% |
| No major events | STAY_OUT | MEDIUM | 65% |

## Testing Workflow

### 1. Test Frontend with Mock Data
```bash
# In .env
DISABLE_AI=true

# Run backend
cd backend
python demo_v2.py

# Run frontend
cd frontend
npm run dev
```

You'll see mock recommendations with `[MOCK]` labels in the dashboard.

### 2. Test with Real AI
```bash
# In .env
DISABLE_AI=false

# Same commands as above
```

You'll see real Gemini AI analysis (uses API quota).

## Benefits

✅ **No API costs during testing** - Mock mode is completely free
✅ **Realistic data** - Mock recommendations follow same JSON schema
✅ **Event-driven** - Mock urgency/type changes based on detected events
✅ **Easy toggle** - Just one line in `.env`
✅ **Frontend compatible** - Frontend can't tell the difference (except for `[MOCK]` labels)

## Terminal Output

### AI Disabled:
```
🤖 Calling AI Coordinator (API Call #1)...
[MOCK MODE] AI disabled - returning mock recommendation
```

### AI Enabled:
```
🤖 Calling AI Coordinator (API Call #1)...
[Makes real Gemini API call]
```

## Quick Reference

**Enable AI:**
```bash
# Remove or set to false
DISABLE_AI=false
```

**Disable AI:**
```bash
# Set to true
DISABLE_AI=true
```

**Current status in code:**
```python
from coordinator_agent import DISABLE_AI
print(f"AI is {'disabled' if DISABLE_AI else 'enabled'}")
```
