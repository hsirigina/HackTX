"""
Data Agents - Pure Python analysis with minimal AI calls
4 specialized agents that detect events and synthesize data for the AI Coordinator
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics
from tire_model import TireDegradationModel


class TriggerEvent:
    """Represents a detected event that may warrant AI analysis"""
    def __init__(self, event_type: str, urgency: str, data: Dict, call_ai: bool = False):
        self.type = event_type
        self.urgency = urgency  # CRITICAL, HIGH, MEDIUM, LOW
        self.data = data
        self.call_ai = call_ai
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'urgency': self.urgency,
            'data': self.data,
            'call_ai': self.call_ai,
            'timestamp': self.timestamp.isoformat()
        }


class TireDataAgent:
    """
    Monitors tire degradation, predicts cliff, detects pit stops
    Pure Python - no AI calls
    """
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.last_compound = None
        self.last_tire_age = 0
        self.last_ai_call_lap = 0
        self.tire_history = []  # Track degradation over time
        self.tire_model = TireDegradationModel(total_laps=78)

    def analyze(self, lap_data: Dict, current_lap: int) -> List[TriggerEvent]:
        """
        Detect tire-related events

        Args:
            lap_data: {
                'compound': str,
                'tire_age': int,
                'lap_time': float,
                'track_temp': float (optional)
            }
            current_lap: int

        Returns:
            List of TriggerEvents
        """
        events = []

        compound = lap_data.get('compound')
        tire_age = lap_data.get('tire_age', 0)
        lap_time = lap_data.get('lap_time')
        track_temp = lap_data.get('track_temp', 30.0)

        # Store for trend analysis
        self.tire_history.append({
            'lap': current_lap,
            'compound': compound,
            'age': tire_age,
            'lap_time': lap_time
        })

        # CRITICAL: Tire change detected
        if self.last_compound and compound != self.last_compound:
            events.append(TriggerEvent(
                event_type='PIT_STOP',
                urgency='CRITICAL',
                call_ai=True,
                data={
                    'old_compound': self.last_compound,
                    'new_compound': compound,
                    'lap': current_lap,
                    'message': f"Pit stop: {self.last_compound} → {compound}"
                }
            ))

        # CRITICAL: Tire age reset (pit stop without compound change)
        if tire_age < self.last_tire_age - 5:  # Age jumped backward
            events.append(TriggerEvent(
                event_type='PIT_STOP',
                urgency='CRITICAL',
                call_ai=True,
                data={
                    'compound': compound,
                    'new_age': tire_age,
                    'lap': current_lap,
                    'message': f"Pit stop detected (tire age reset to {tire_age})"
                }
            ))

        # CRITICAL: Tire cliff imminent
        if compound and tire_age > 0:
            wear_rate = self.tire_model.get_tire_wear_rate(compound, tire_age)
            degradation = wear_rate * (tire_age - 1)  # Total degradation from fresh

            if degradation > 2.0 and tire_age > 15:
                # Predict cliff lap
                cliff_lap = self._predict_cliff_lap(compound, track_temp)

                events.append(TriggerEvent(
                    event_type='TIRE_CLIFF',
                    urgency='CRITICAL',
                    call_ai=True,
                    data={
                        'degradation': round(degradation, 2),
                        'age': tire_age,
                        'compound': compound,
                        'predicted_cliff_lap': cliff_lap,
                        'laps_until_cliff': cliff_lap - tire_age if cliff_lap else None,
                        'message': f"Tire cliff imminent! +{degradation:.1f}s degradation at {tire_age} laps"
                    }
                ))

        # HIGH: Old tires - analyze more frequently
        if tire_age > 20:
            laps_since = current_lap - self.last_ai_call_lap
            if laps_since >= 3:
                wear_rate = self.tire_model.get_tire_wear_rate(compound, tire_age)
                deg = wear_rate * (tire_age - 1)
                events.append(TriggerEvent(
                    event_type='OLD_TIRES',
                    urgency='HIGH',
                    call_ai=True,
                    data={
                        'age': tire_age,
                        'compound': compound,
                        'degradation': round(deg, 2),
                        'message': f"Old tires ({tire_age} laps on {compound})"
                    }
                ))

        # MEDIUM: Periodic tire check
        if not events:  # Only if no other events triggered
            laps_since = current_lap - self.last_ai_call_lap
            if laps_since >= 10:
                events.append(TriggerEvent(
                    event_type='PERIODIC_TIRE',
                    urgency='MEDIUM',
                    call_ai=True,
                    data={
                        'age': tire_age,
                        'compound': compound,
                        'message': 'Periodic tire status check'
                    }
                ))

        # Update state
        self.last_compound = compound
        self.last_tire_age = tire_age
        if events and any(e.call_ai for e in events):
            self.last_ai_call_lap = current_lap

        return events

    def _predict_cliff_lap(self, compound: str, track_temp: float) -> Optional[int]:
        """Predict when tire will hit cliff (degradation > 3.0s)"""
        # Returns tire age when cliff occurs, NOT race lap number
        return self.tire_model.predict_tire_cliff(compound, threshold=3.0)

    def get_status_summary(self) -> Dict:
        """Return current tire status for AI context"""
        if not self.tire_history:
            return {}

        latest = self.tire_history[-1]

        # Calculate degradation trend (last 5 laps)
        if len(self.tire_history) >= 5:
            recent_times = [h['lap_time'] for h in self.tire_history[-5:] if h['lap_time']]
            if recent_times:
                trend = recent_times[-1] - recent_times[0]
            else:
                trend = 0
        else:
            trend = 0

        # Get predicted cliff tire age
        predicted_cliff_age = self._predict_cliff_lap(latest['compound'], 30.0)

        # Calculate laps remaining until cliff (not absolute lap number)
        laps_until_cliff = predicted_cliff_age - latest['age'] if predicted_cliff_age else None

        return {
            'current_compound': latest['compound'],
            'tire_age': latest['age'],
            'degradation_trend_5_laps': round(trend, 2),
            'predicted_cliff_age': predicted_cliff_age,  # Tire age when cliff occurs
            'laps_until_cliff': laps_until_cliff  # How many more laps until cliff
        }


class LapTimeAgent:
    """
    Monitors lap times, detects pace changes, identifies degradation patterns
    Pure Python - no AI calls
    """
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.lap_times = []
        self.last_ai_call_lap = 0

    def analyze(self, lap_data: Dict, current_lap: int) -> List[TriggerEvent]:
        """
        Detect pace-related events

        Args:
            lap_data: {
                'lap_time': float,
                'sector1': float,
                'sector2': float,
                'sector3': float
            }
            current_lap: int

        Returns:
            List of TriggerEvents
        """
        events = []

        lap_time = lap_data.get('lap_time')
        if not lap_time:
            return events

        self.lap_times.append({
            'lap': current_lap,
            'time': lap_time,
            'sector1': lap_data.get('sector1'),
            'sector2': lap_data.get('sector2'),
            'sector3': lap_data.get('sector3')
        })

        # Need at least 5 laps for meaningful analysis
        if len(self.lap_times) < 5:
            return events

        recent_laps = [lt['time'] for lt in self.lap_times[-5:]]

        # CRITICAL: Pace collapse
        avg_early = statistics.mean(recent_laps[:2])
        avg_recent = statistics.mean(recent_laps[-2:])
        delta = avg_recent - avg_early

        if delta > 1.5:
            events.append(TriggerEvent(
                event_type='PACE_COLLAPSE',
                urgency='CRITICAL',
                call_ai=True,
                data={
                    'delta': round(delta, 2),
                    'avg_early': round(avg_early, 2),
                    'avg_recent': round(avg_recent, 2),
                    'recent_laps': [round(t, 2) for t in recent_laps],
                    'message': f"Pace collapse: +{delta:.1f}s over 5 laps"
                }
            ))

        # HIGH: Degradation accelerating
        if len(self.lap_times) >= 4:
            lap_deltas = [
                self.lap_times[i]['time'] - self.lap_times[i-1]['time']
                for i in range(-3, 0)
            ]

            # Check if last 3 laps are progressively slower
            if all(d > 0.2 for d in lap_deltas):  # Each lap 0.2s slower
                events.append(TriggerEvent(
                    event_type='DEGRADATION_ACCELERATING',
                    urgency='HIGH',
                    call_ai=True,
                    data={
                        'deltas': [round(d, 2) for d in lap_deltas],
                        'message': 'Pace degrading consistently over last 3 laps'
                    }
                ))

        # LOW: Just update pace trend (no AI call)
        events.append(TriggerEvent(
            event_type='PACE_UPDATE',
            urgency='LOW',
            call_ai=False,
            data={
                'current_lap_time': round(lap_time, 2),
                'avg_last_5': round(statistics.mean(recent_laps), 2)
            }
        ))

        return events

    def get_status_summary(self) -> Dict:
        """Return pace analysis for AI context"""
        if len(self.lap_times) < 3:
            return {}

        recent_5 = [lt['time'] for lt in self.lap_times[-5:]]
        all_times = [lt['time'] for lt in self.lap_times]

        # Calculate pace trend (positive = getting slower, negative = getting faster)
        pace_trend = round(recent_5[-1] - recent_5[0], 3) if len(recent_5) >= 2 else 0

        return {
            'current_pace': round(self.lap_times[-1]['time'], 3),  # Latest lap time
            'avg_lap_time': round(statistics.mean(all_times), 2),
            'avg_last_5_laps': round(statistics.mean(recent_5), 2),
            'pace_trend': pace_trend,  # How much slower/faster over last 5 laps
            'best_lap': round(min(all_times), 2),
            'worst_lap': round(max(all_times), 2),
            'trend': 'degrading' if recent_5[-1] > recent_5[0] else 'stable'
        }


class PositionAgent:
    """
    Monitors race position, gaps to competitors, detects position changes
    Pure Python - no AI calls
    """
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.last_position = None
        self.position_history = []
        self.last_ai_call_lap = 0

    def analyze(self, position_data: Dict, current_lap: int) -> List[TriggerEvent]:
        """
        Detect position-related events

        Args:
            position_data: {
                'position': int,
                'gap_ahead': float (seconds),
                'gap_behind': float (seconds)
            }
            current_lap: int

        Returns:
            List of TriggerEvents
        """
        events = []

        position = position_data.get('position')
        gap_ahead = position_data.get('gap_ahead', 999)
        gap_behind = position_data.get('gap_behind', 999)

        self.position_history.append({
            'lap': current_lap,
            'position': position,
            'gap_ahead': gap_ahead,
            'gap_behind': gap_behind
        })

        # CRITICAL: Position change
        if self.last_position and position and position != self.last_position:
            change = self.last_position - position  # Positive = gained positions

            events.append(TriggerEvent(
                event_type='POSITION_CHANGE',
                urgency='CRITICAL',
                call_ai=True,
                data={
                    'old_position': self.last_position,
                    'new_position': position,
                    'change': change,
                    'message': f"Position change: P{self.last_position} → P{position} ({'+' if change > 0 else ''}{change})"
                }
            ))

        # HIGH: Top 3 racing with close gaps
        if position and position <= 3:
            if (gap_ahead is not None and gap_ahead < 2.0) or (gap_behind is not None and gap_behind < 2.0):
                laps_since = current_lap - self.last_ai_call_lap
                if laps_since >= 5:  # Don't spam for top 3
                    events.append(TriggerEvent(
                        event_type='CLOSE_RACING',
                        urgency='HIGH',
                        call_ai=True,
                        data={
                            'position': position,
                            'gap_ahead': round(gap_ahead, 2) if gap_ahead is not None else None,
                            'gap_behind': round(gap_behind, 2) if gap_behind is not None else None,
                            'message': f"Close racing: P{position} with gaps <2s (ahead: {gap_ahead:.1f}s, behind: {gap_behind:.1f}s)"
                        }
                    ))

        # HIGH: Gap closing rapidly
        if len(self.position_history) >= 3:
            prev_gap_ahead = self.position_history[-3]['gap_ahead']
            if prev_gap_ahead is not None and prev_gap_ahead < 999 and gap_ahead is not None and gap_ahead < 999:
                gap_change = prev_gap_ahead - gap_ahead  # Positive = closing

                if gap_change > 1.0:  # Closed 1+ seconds in 2 laps
                    events.append(TriggerEvent(
                        event_type='GAP_CLOSING',
                        urgency='HIGH',
                        call_ai=True,
                        data={
                            'gap_ahead': round(gap_ahead, 2),
                            'gap_change': round(gap_change, 2),
                            'message': f"Closing on car ahead: gap reduced by {gap_change:.1f}s"
                        }
                    ))

        # LOW: Position update (no AI call)
        events.append(TriggerEvent(
            event_type='POSITION_UPDATE',
            urgency='LOW',
            call_ai=False,
            data={
                'position': position,
                'gap_ahead': round(gap_ahead, 2) if gap_ahead is not None and gap_ahead < 999 else None,
                'gap_behind': round(gap_behind, 2) if gap_behind is not None and gap_behind < 999 else None
            }
        ))

        # Update state
        self.last_position = position
        if events and any(e.call_ai for e in events):
            self.last_ai_call_lap = current_lap

        return events

    def get_status_summary(self) -> Dict:
        """Return position analysis for AI context"""
        if not self.position_history:
            return {}

        latest = self.position_history[-1]

        # Calculate position trend
        if len(self.position_history) >= 5:
            positions = [h['position'] for h in self.position_history[-5:]]
            trend = 'improving' if positions[-1] < positions[0] else 'declining' if positions[-1] > positions[0] else 'stable'
        else:
            trend = 'stable'

        return {
            'current_position': latest['position'],
            'gap_ahead': round(latest['gap_ahead'], 2) if latest['gap_ahead'] is not None and latest['gap_ahead'] < 999 else None,
            'gap_behind': round(latest['gap_behind'], 2) if latest['gap_behind'] is not None and latest['gap_behind'] < 999 else None,
            'trend': trend
        }


class CompetitorAgent:
    """
    Monitors nearby competitors, detects their pit stops, compares pace
    Pure Python - no AI calls
    """
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.competitor_history = {}  # driver_name -> list of data
        self.last_ai_call_lap = 0

    def analyze(self, our_data: Dict, all_drivers: List[Dict], current_lap: int) -> List[TriggerEvent]:
        """
        Detect competitor-related events

        Args:
            our_data: {
                'position': int,
                'lap_time': float,
                'tire_age': int
            }
            all_drivers: List[{
                'name': str,
                'position': int,
                'lap_time': float,
                'tire_age': int,
                'compound': str
            }]
            current_lap: int

        Returns:
            List of TriggerEvents
        """
        events = []

        our_position = our_data.get('position')
        our_lap_time = our_data.get('lap_time')
        our_tire_age = our_data.get('tire_age', 0)

        # Return early if we don't have valid position data
        if our_position is None:
            return events

        # Define "nearby" as P±2
        nearby_range = range(
            max(1, our_position - 2),
            min(21, our_position + 3)
        )

        for driver in all_drivers:
            if driver['name'] == self.driver_name:
                continue

            driver_name = driver['name']
            driver_position = driver.get('position')
            driver_lap_time = driver.get('lap_time')
            driver_tire_age = driver.get('tire_age', 0)

            # Track history
            if driver_name not in self.competitor_history:
                self.competitor_history[driver_name] = []

            self.competitor_history[driver_name].append({
                'lap': current_lap,
                'position': driver_position,
                'lap_time': driver_lap_time,
                'tire_age': driver_tire_age,
                'compound': driver.get('compound')
            })

            # Only analyze nearby competitors
            if driver_position not in nearby_range:
                continue

            # CRITICAL: Competitor pit stop
            if len(self.competitor_history[driver_name]) >= 2:
                prev = self.competitor_history[driver_name][-2]

                # Tire age reset = pit stop
                if driver_tire_age < prev['tire_age'] - 5:
                    events.append(TriggerEvent(
                        event_type='COMPETITOR_PIT',
                        urgency='CRITICAL',
                        call_ai=True,
                        data={
                            'driver': driver_name,
                            'position': driver_position,
                            'our_position': our_position,
                            'new_tire_age': driver_tire_age,
                            'message': f"{driver_name} (P{driver_position}) just pitted - undercut/overcut opportunity"
                        }
                    ))

            # HIGH: Competitor pace advantage
            if our_lap_time and driver_lap_time:
                pace_delta = our_lap_time - driver_lap_time  # Positive = they're faster

                if pace_delta > 0.5:  # They're 0.5s/lap faster
                    events.append(TriggerEvent(
                        event_type='COMPETITOR_FASTER',
                        urgency='HIGH',
                        call_ai=True,
                        data={
                            'driver': driver_name,
                            'position': driver_position,
                            'pace_delta': round(pace_delta, 2),
                            'our_pace': round(our_lap_time, 2),
                            'their_pace': round(driver_lap_time, 2),
                            'message': f"{driver_name} (P{driver_position}) is {pace_delta:.1f}s/lap faster"
                        }
                    ))

        # MEDIUM: Periodic competitor check
        if not events:
            laps_since = current_lap - self.last_ai_call_lap
            if laps_since >= 15:
                events.append(TriggerEvent(
                    event_type='PERIODIC_COMPETITOR',
                    urgency='MEDIUM',
                    call_ai=True,
                    data={
                        'message': 'Periodic competitor analysis'
                    }
                ))

        # Update state
        if events and any(e.call_ai for e in events):
            self.last_ai_call_lap = current_lap

        return events

    def get_status_summary(self, our_position: int) -> Dict:
        """Return competitor analysis for AI context"""
        # Handle None position
        if our_position is None:
            return {
                'nearby_competitors': [],
                'threats': [],
                'opportunities': []
            }

        nearby_range = range(max(1, our_position - 2), min(21, our_position + 3))

        nearby_competitors = []
        for driver_name, history in self.competitor_history.items():
            if history:
                latest = history[-1]
                if latest['position'] in nearby_range:
                    nearby_competitors.append({
                        'name': driver_name,
                        'position': latest['position'],
                        'tire_age': latest['tire_age'],
                        'compound': latest['compound']
                    })

        # Sort by position
        nearby_competitors.sort(key=lambda x: x['position'])

        # Identify threats (cars behind on fresher tires or faster pace)
        threats = []
        for c in nearby_competitors:
            if c['position'] > our_position:  # Car behind us
                if c['tire_age'] < 10:
                    threats.append({
                        'driver': c['name'],
                        'position': c['position'],
                        'message': f"Fresh tires ({c['tire_age']} laps old) - {c['compound']}"
                    })

        # Identify opportunities (cars ahead on older tires or slower pace)
        opportunities = []
        for c in nearby_competitors:
            if c['position'] < our_position:  # Car ahead of us
                if c['tire_age'] > 30:
                    opportunities.append({
                        'driver': c['name'],
                        'position': c['position'],
                        'message': f"Old tires ({c['tire_age']} laps) - {c['compound']}"
                    })

        return {
            'nearby_competitors': nearby_competitors,
            'threats': threats,
            'opportunities': opportunities
        }


class EventDetector:
    """
    Aggregates events from all data agents and decides when to call AI Coordinator
    """
    def __init__(self):
        self.priority_map = {
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4
        }

    def check_triggers(self, all_events: List[TriggerEvent]) -> Tuple[bool, List[TriggerEvent]]:
        """
        Determine if AI Coordinator should be called

        Args:
            all_events: Combined events from all 4 data agents

        Returns:
            (should_call_ai, sorted_events)
        """
        if not all_events:
            return False, []

        # Sort by urgency
        sorted_events = sorted(all_events, key=lambda e: self.priority_map[e.urgency])

        # CRITICAL events always trigger AI
        if any(e.urgency == 'CRITICAL' for e in all_events):
            return True, sorted_events

        # Multiple HIGH events trigger AI
        high_events = [e for e in all_events if e.urgency == 'HIGH']
        if len(high_events) >= 2:
            return True, sorted_events

        # Single HIGH event that explicitly requests AI
        if any(e.urgency == 'HIGH' and e.call_ai for e in all_events):
            return True, sorted_events

        # MEDIUM events that explicitly request AI
        if any(e.urgency == 'MEDIUM' and e.call_ai for e in all_events):
            return True, sorted_events

        return False, sorted_events

    def format_events_for_ai(self, events: List[TriggerEvent]) -> str:
        """Format events as context for AI Coordinator"""
        if not events:
            return "No significant events detected."

        lines = ["**Detected Events:**\n"]

        for event in events:
            if event.urgency in ['CRITICAL', 'HIGH']:
                urgency_icon = "🔴" if event.urgency == 'CRITICAL' else "🟡"
                message = event.data.get('message', event.type)
                lines.append(f"{urgency_icon} [{event.urgency}] {message}")

        return "\n".join(lines)
