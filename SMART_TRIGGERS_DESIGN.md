# Smart Triggers Design - Data-Driven Event Detection

## Overview

With the new architecture (4 Data Agents + 1 AI Coordinator), **smart triggers** determine when to call the expensive AI Coordinator. Data agents run continuously (they're free!), detecting events that warrant strategic analysis.

## Available Data from FastF1

### ✅ What We Have Access To:

| Data Field | Source | Update Frequency | Use Case |
|------------|--------|------------------|----------|
| **LapTime** | lap_times table | Every lap | Pace degradation detection |
| **Sector1/2/3Time** | lap_times table | Every lap | Micro-pace analysis |
| **Compound** | tire_data table | Every lap | Tire change detection |
| **TyreLife** (age) | tire_data table | Every lap | Degradation prediction |
| **Position** | race_positions table | Every lap | Position change detection |
| **PitInTime/PitOutTime** | pit_stops table | On pit | Pit stop event detection |
| **SpeedI1/I2/ST/FL** | FastF1 (not stored yet) | Every lap | Speed trap comparison |

### ❌ What We DON'T Have:

- Real-time weather/radar
- Track temperature (we can approximate)
- Tire pressure
- Brake temperatures
- G-forces
- Telemetry data (throttle, brake inputs)

**Good news:** We have everything needed for strategic F1 decisions! 🎉

---

## Smart Trigger System Architecture

### **Flow:**

```
Every Lap:
  ├─ Data Agents run (FREE - pure Python)
  │   ├─ TireDataAgent.analyze() → detects events
  │   ├─ LapTimeAgent.analyze() → detects events
  │   ├─ PositionAgent.analyze() → detects events
  │   └─ CompetitorAgent.analyze() → detects events
  │
  ├─ EventDetector.check_triggers()
  │   └─ IF any critical event detected:
  │       └─ Coordinator.analyze() → 1 Gemini API call
  │
  └─ Display updates (always, using latest data)
```

---

## Trigger Categories

### **1. CRITICAL Triggers (Always call AI)**

These events **always** warrant strategic analysis:

| Event | Detection Method | Data Used |
|-------|------------------|-----------|
| **Pit Stop Occurred** | Compound changed OR TyreLife reset | `compound`, `tire_age` |
| **Position Change** | Position != last_position | `position` |
| **Tire Cliff Imminent** | Degradation > 2.0s AND age > 15 | Local tire model + `lap_times` |
| **Competitor Pit Stop** | PitOutTime not null for P±2 | `pit_stops` + `race_positions` |
| **Pace Collapse** | Lap time +1.5s slower than 5-lap avg | `lap_times` |

**Example:**
```python
# TireDataAgent detects
if tire_age != last_tire_age - 1:  # Jump in age = pit stop
    return TriggerEvent(
        type="PIT_STOP",
        urgency="CRITICAL",
        reason="Tire change detected",
        call_ai=True
    )
```

### **2. HIGH Triggers (Call AI if recent data)**

Important but not urgent - call AI if last analysis was >5 laps ago:

| Event | Detection Method | Threshold |
|-------|------------------|-----------|
| **Old Tires** | tire_age > 20 | Age threshold |
| **Top 3 Racing** | position <= 3 | Position threshold |
| **Gap Closing** | Gap to P±1 < 2.0s | Position delta |
| **Degradation Accelerating** | Δ pace increasing lap-over-lap | Lap time trend |

**Example:**
```python
# PositionAgent detects
if position <= 3:
    laps_since_last = current_lap - last_ai_call_lap
    if laps_since_last >= 5:
        return TriggerEvent(
            type="TOP_3_RACING",
            urgency="HIGH",
            reason="Close racing in podium positions",
            call_ai=True
        )
```

### **3. MEDIUM Triggers (Periodic review)**

Regular checks - call AI if >10 laps since last analysis:

| Event | Detection Method |
|-------|------------------|
| **Periodic Tire Check** | Every 10 laps |
| **Periodic Competitor Check** | Every 15 laps |
| **Full Strategy Review** | Every 20 laps |

### **4. LOW Triggers (Data only, no AI)**

These update the display but don't call AI:

| Event | Action |
|-------|--------|
| Lap completed | Update display lap counter |
| New lap time | Update pace trend graph |
| Gap changed | Update position display |

---

## Detailed Trigger Logic

### **Tire Data Agent Triggers**

```python
class TireDataAgent:
    def detect_events(self, lap_data):
        events = []

        # CRITICAL: Tire change
        if lap_data['compound'] != self.last_compound:
            events.append({
                'type': 'PIT_STOP',
                'urgency': 'CRITICAL',
                'call_ai': True,
                'data': {
                    'old_compound': self.last_compound,
                    'new_compound': lap_data['compound'],
                    'message': f"Pit stop: {self.last_compound} → {lap_data['compound']}"
                }
            })

        # CRITICAL: Tire cliff imminent
        degradation = self.tire_model.get_degradation_rate(
            lap_data['compound'],
            lap_data['tire_age']
        )
        if degradation > 2.0 and lap_data['tire_age'] > 15:
            events.append({
                'type': 'TIRE_CLIFF',
                'urgency': 'CRITICAL',
                'call_ai': True,
                'data': {
                    'degradation': degradation,
                    'age': lap_data['tire_age'],
                    'cliff_lap': self.tire_model.predict_tire_cliff(lap_data['compound']),
                    'message': f"Tire cliff imminent! +{degradation:.1f}s degradation"
                }
            })

        # HIGH: Old tires
        if lap_data['tire_age'] > 20:
            laps_since = lap_data['lap_number'] - self.last_ai_call
            if laps_since >= 3:
                events.append({
                    'type': 'OLD_TIRES',
                    'urgency': 'HIGH',
                    'call_ai': True,
                    'data': {
                        'age': lap_data['tire_age'],
                        'message': f"Old tires ({lap_data['tire_age']} laps)"
                    }
                })

        # MEDIUM: Periodic check
        laps_since = lap_data['lap_number'] - self.last_ai_call
        if laps_since >= 10 and not events:
            events.append({
                'type': 'PERIODIC_TIRE',
                'urgency': 'MEDIUM',
                'call_ai': True,
                'data': {'message': 'Periodic tire check'}
            })

        return events
```

### **Lap Time Agent Triggers**

```python
class LapTimeAgent:
    def detect_events(self, recent_laps):
        events = []

        # Calculate trend
        if len(recent_laps) >= 5:
            avg_early = sum(recent_laps[:2]) / 2
            avg_recent = sum(recent_laps[-2:]) / 2
            delta = avg_recent - avg_early

            # CRITICAL: Pace collapse
            if delta > 1.5:
                events.append({
                    'type': 'PACE_COLLAPSE',
                    'urgency': 'CRITICAL',
                    'call_ai': True,
                    'data': {
                        'delta': delta,
                        'trend': recent_laps,
                        'message': f"Pace collapse: +{delta:.1f}s over 5 laps"
                    }
                })

            # HIGH: Degradation accelerating
            lap_deltas = [recent_laps[i] - recent_laps[i-1] for i in range(1, len(recent_laps))]
            if all(d > 0 for d in lap_deltas[-3:]):  # 3 laps getting progressively slower
                events.append({
                    'type': 'DEGRADATION_ACCELERATING',
                    'urgency': 'HIGH',
                    'call_ai': True,
                    'data': {
                        'deltas': lap_deltas,
                        'message': 'Pace degrading consistently'
                    }
                })

        return events
```

### **Position Agent Triggers**

```python
class PositionAgent:
    def detect_events(self, position_data):
        events = []

        # CRITICAL: Position change
        if position_data['position'] != self.last_position:
            events.append({
                'type': 'POSITION_CHANGE',
                'urgency': 'CRITICAL',
                'call_ai': True,
                'data': {
                    'old_position': self.last_position,
                    'new_position': position_data['position'],
                    'message': f"Position change: P{self.last_position} → P{position_data['position']}"
                }
            })

        # HIGH: Top 3 racing
        if position_data['position'] <= 3:
            gap_ahead = position_data.get('gap_ahead', 999)
            gap_behind = position_data.get('gap_behind', 999)

            if gap_ahead < 2.0 or gap_behind < 2.0:
                events.append({
                    'type': 'CLOSE_RACING',
                    'urgency': 'HIGH',
                    'call_ai': True,
                    'data': {
                        'position': position_data['position'],
                        'gap_ahead': gap_ahead,
                        'gap_behind': gap_behind,
                        'message': f"Close racing: P{position_data['position']} with <2s gaps"
                    }
                })

        return events
```

### **Competitor Agent Triggers**

```python
class CompetitorAgent:
    def detect_events(self, our_data, all_drivers):
        events = []

        # CRITICAL: Nearby competitor pit stop
        nearby_positions = range(
            max(1, our_data['position'] - 2),
            min(20, our_data['position'] + 2)
        )

        for driver in all_drivers:
            if driver['position'] in nearby_positions and driver['just_pitted']:
                events.append({
                    'type': 'COMPETITOR_PIT',
                    'urgency': 'CRITICAL',
                    'call_ai': True,
                    'data': {
                        'driver': driver['name'],
                        'position': driver['position'],
                        'our_position': our_data['position'],
                        'message': f"{driver['name']} (P{driver['position']}) just pitted - undercut/overcut opportunity"
                    }
                })

        # HIGH: Competitor pace advantage
        for driver in all_drivers:
            if abs(driver['position'] - our_data['position']) <= 2:
                pace_delta = our_data['lap_time'] - driver['lap_time']
                if pace_delta > 0.5:  # They're 0.5s/lap faster
                    events.append({
                        'type': 'COMPETITOR_FASTER',
                        'urgency': 'HIGH',
                        'call_ai': True,
                        'data': {
                            'driver': driver['name'],
                            'pace_delta': pace_delta,
                            'message': f"{driver['name']} is {pace_delta:.1f}s/lap faster"
                        }
                    })

        return events
```

---

## Event Prioritization

When multiple events occur on the same lap:

```python
def prioritize_events(events):
    priority = {
        'CRITICAL': 1,
        'HIGH': 2,
        'MEDIUM': 3,
        'LOW': 4
    }

    # Sort by urgency
    sorted_events = sorted(events, key=lambda e: priority[e['urgency']])

    # If any CRITICAL event, call AI immediately
    if any(e['urgency'] == 'CRITICAL' for e in events):
        return True, sorted_events

    # If multiple HIGH events, call AI
    high_events = [e for e in events if e['urgency'] == 'HIGH']
    if len(high_events) >= 2:
        return True, sorted_events

    # Otherwise, check periodic triggers
    return check_periodic_triggers(), sorted_events
```

---

## Example: Monaco Lap 65

**Data from FastF1:**
```
LEC:
  - Lap: 65
  - Position: 1
  - LapTime: 76.607s
  - Compound: HARD
  - TyreLife: 64 laps
  - Gap behind: +0.8s (Piastri)
```

**Data Agents Analyze:**

1. **TireDataAgent:**
   - Tire age: 64 laps (very old!)
   - Degradation: +2.3s vs fresh
   - **Event: OLD_TIRES (HIGH urgency)**

2. **LapTimeAgent:**
   - Last 5 laps: [76.4, 76.5, 76.6, 76.6, 76.6]
   - Trend: Stable but slow
   - **Event: None (stable pace)**

3. **PositionAgent:**
   - Position: P1 (same as last lap)
   - Gap: 0.8s to P2 (closing!)
   - **Event: CLOSE_RACING (HIGH urgency)**

4. **CompetitorAgent:**
   - Piastri (P2): 0.3s/lap faster
   - **Event: COMPETITOR_FASTER (HIGH urgency)**

**Trigger Decision:**
- 3 HIGH urgency events detected
- Last AI call: Lap 60 (5 laps ago)
- **Decision: CALL AI COORDINATOR** ✅

**AI Coordinator receives:**
```json
{
  "lap": 65,
  "driver": "LEC",
  "events": [
    {"type": "OLD_TIRES", "urgency": "HIGH", "data": {...}},
    {"type": "CLOSE_RACING", "urgency": "HIGH", "data": {...}},
    {"type": "COMPETITOR_FASTER", "urgency": "HIGH", "data": {...}}
  ],
  "tire_status": {...},
  "pace_trend": {...},
  "position_context": {...},
  "competitor_analysis": {...}
}
```

**AI synthesizes:** "Critical situation. Tires at limit (64 laps), Piastri closing. Recommendation: Maintain pace, defend position, avoid mistakes. Tires will last to finish but no margin for error."

---

## Threshold Summary

| Metric | Threshold | Trigger Type |
|--------|-----------|--------------|
| Tire degradation | > 2.0s | CRITICAL |
| Tire age | > 20 laps | HIGH |
| Tire age | > 30 laps | Analyze every 3 laps |
| Pace delta | +1.5s vs avg | CRITICAL (collapse) |
| Position change | Any | CRITICAL |
| Gap to nearby car | < 2.0s | HIGH |
| Competitor pace | +0.5s/lap faster | HIGH |
| Laps since analysis | 10 laps (tire) | MEDIUM |
| Laps since analysis | 15 laps (competitor) | MEDIUM |
| Laps since analysis | 20 laps (full) | MEDIUM |

---

## Benefits of This Approach

✅ **Data agents run every lap (free!)** - Continuous monitoring
✅ **AI only called when needed** - Cost effective
✅ **Rich context for AI** - Data agents pre-process everything
✅ **Deterministic triggers** - Easy to test and debug
✅ **Responsive to events** - Feels "live"
✅ **Efficient** - ~8-12 AI calls per race

---

## Implementation Checklist

- [ ] Create EventDetector class
- [ ] Implement trigger logic in each data agent
- [ ] Build event prioritization system
- [ ] Update race monitor to use events
- [ ] Test thresholds with historical data
- [ ] Tune thresholds for optimal triggering

This gives you **intelligent, data-driven triggering** using the rich FastF1 data we already have! 🎯
