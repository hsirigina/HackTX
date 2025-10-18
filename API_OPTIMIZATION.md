# API Call Optimization Strategy

## Problem

**Gemini Free Tier Limits:**
- 15 requests per minute (RPM)
- 1,500 requests per day (RPD)

**Original Approach:**
- 3 agents × every lap = 3 API calls per lap
- Monaco 78 laps = 234 API calls
- **Result: Exceeds daily limit!**

**Every 5 Laps:**
- ~47 API calls for full race
- **Result: Works but not very "live"**

## Solution: Smart Event-Based Triggering

Instead of calling agents on a fixed schedule, we trigger them intelligently based on **race events**:

### Tire Agent Triggers

| Event | Frequency | Why |
|-------|-----------|-----|
| Tire compound changed | Immediate | Pit stop happened! |
| Tire age reset | Immediate | Pit stop detected |
| Tire age > 20 laps | Every 3 laps | Old tires degrade faster |
| Default | Every 10 laps | Periodic check |

### Competitor Agent Triggers

| Event | Frequency | Why |
|-------|-----------|-----|
| Position in top 3 | Every 5 laps | Close racing matters more |
| Default | Every 15 laps | Periodic check |

### Coordinator Agent Triggers

| Event | When |
|-------|------|
| Both agents ran | Same lap | Fresh data to synthesize |
| Default | Every 20 laps | Full strategy review |

## Results

**For Monaco 2024 (78 laps):**

### Original (Every Lap)
- API Calls: **234**
- Result: ❌ Exceeds daily limit

### Every 5 Laps
- API Calls: **~47**
- Result: ✅ Works but not responsive

### Smart Event-Based
- API Calls: **~25-35** (depending on pit stops)
- Result: ✅✅ Responsive AND efficient!

## API Call Breakdown Example

**Monaco 2024, Laps 60-78 (Final Stint):**

```
Lap 60: ✓ Tire (periodic check)
Lap 61: -
Lap 62: -
Lap 63: -
Lap 64: -
Lap 65: ✓ Competitor (top 3 check)
Lap 66: -
Lap 67: -
Lap 68: -
Lap 69: -
Lap 70: ✓ Tire (periodic), ✓ Coordinator (both agents ran)
Lap 71: -
Lap 72: -
Lap 73: -
Lap 74: -
Lap 75: ✓ Competitor (top 3 check)
Lap 76: -
Lap 77: -
Lap 78: ✓ Tire (periodic)

Total for 19 laps: ~8 API calls
(vs 57 calls if every lap, vs 12 if every 5 laps)
```

## Cache Strategy

Between triggers, agents **reuse cached recommendations**:

```python
# First analysis
lap 10: Tire Agent runs → "Tires OK, good for 10 more laps"

# Cache reused
lap 11-19: Dashboard shows cached "Tires OK" message

# New analysis
lap 20: Tire Agent runs again → "Tire deg increasing, pit soon"
```

This gives the **illusion of live monitoring** without burning API calls!

## Additional Optimizations

### 1. Batch Processing (Not Implemented Yet)
Instead of 3 separate API calls, combine into one:
```python
# Single call with all context
prompt = f"""
You are coordinating 3 agents:
1. Tire analysis: {tire_context}
2. Competitor analysis: {comp_context}
3. Synthesis: {race_context}

Provide all 3 outputs in JSON...
"""
```
**Savings: 3 calls → 1 call per analysis**

### 2. Local Tire Model (Already Implemented)
We ported the MATLAB tire degradation model to Python:
- Optimal pit window calculations run **locally**
- No API calls needed for basic tire analysis
- Agents only called for **strategic reasoning**

### 3. Streaming Responses (Not Implemented)
Use Gemini's streaming API for faster perceived response:
```python
response = model.generate_content(prompt, stream=True)
for chunk in response:
    # Display partial results immediately
```

## Testing API Usage

Run the demo and monitor calls:

```bash
python demo.py
```

Watch the output:
```
📊 Lap 65 | API Calls: 5
```

At the end:
```
Laps processed: 78
Total API calls: 25
Average: 0.32 calls/lap
```

## Rate Limit Safety

The system stays well under limits:
- **15 RPM limit**: We make ~2-3 calls per minute max
- **1,500 RPD limit**: Full race uses ~25-35 calls

**Margin: 98% of daily limit remaining!**

## For Production

If building a real system:

1. **Use Gemini Pro** (paid tier)
   - 60 RPM
   - 10,000 RPD
   - Better quality responses

2. **Implement request queuing**
   - Queue agent requests
   - Process with rate limiting
   - Prevents burst limit issues

3. **Add exponential backoff**
   ```python
   for attempt in range(3):
       try:
           response = agent.analyze(...)
           break
       except RateLimitError:
           wait = 2 ** attempt  # 1s, 2s, 4s
           time.sleep(wait)
   ```

4. **Cache aggressively**
   - Store agent outputs in database
   - Reuse for similar race conditions
   - "This looks like Bahrain 2023 lap 40..."

## Summary

**Smart Triggering Strategy:**
- ✅ Feels "live" to the user
- ✅ Stays under API limits (98% headroom)
- ✅ Responds to important race events
- ✅ Caches when appropriate

**Key Insight:**
Race strategy doesn't change every lap. We only need fresh analysis when something **meaningful** happens (pit stops, tire wear, position changes). Everything else can use cached recommendations!
