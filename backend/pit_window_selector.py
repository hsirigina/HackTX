"""
Pit Window Selector - New UX for choosing pit stop timing
Instead of "Stay Out vs Pit Now", show a timeline of laps and let user pick WHEN to pit
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PitWindowLap:
    """A single lap in the pit window with AI recommendation strength"""
    lap_number: int
    tire_age_at_lap: int
    tire_compound_before: str

    # Best compound to pit to at this lap
    best_compound: str
    race_time_impact: float  # Total race time impact if pitting this lap

    # Recommendation strength for this specific lap
    recommendation: str  # 'HIGHLY_RECOMMENDED', 'RECOMMENDED', 'ACCEPTABLE', 'NOT_RECOMMENDED'

    # Why this lap?
    reasoning: str

    # Visual indicator
    color: str  # 'green', 'yellow', 'red'


class PitWindowSelector:
    """
    Creates a visual pit window selector showing laps 1-57
    with AI recommendations highlighted

    Instead of:
        Option 1: Pit Now
        Option 2: Stay Out 3 laps
        Option 3: Pit in 5 laps

    Show:
        PIT WINDOW: Laps 18-25 (recommended), 26-30 (risky), 31+ (DANGER!)

        Lap: 18  19  20  21  22  23  24  25  26  27  28  29  30
             🟢  🟢  🟢  🟡  🟡  🔴  🔴  🔴  ⛔  ⛔  ⛔  ⛔  ⛔

        🟢 = RECOMMENDED (optimal window)
        🟡 = ACCEPTABLE (not ideal but ok)
        🔴 = RISKY (approaching cliff)
        ⛔ = DANGER (past cliff)

        User clicks lap 20 → AI confirms "Pitting lap 20 for HARD tires (+35.2s)"
    """

    def __init__(self, tire_model, total_laps: int):
        self.tire_model = tire_model
        self.total_laps = total_laps

    def generate_pit_window(self,
                           current_lap: int,
                           current_tire_age: int,
                           current_compound: str,
                           laps_remaining: int) -> Dict:
        """
        Generate pit window recommendations for next 15 laps

        Returns:
            {
                'current_state': {...},
                'recommended_window': [18, 19, 20],  # Laps to pit (green)
                'acceptable_window': [21, 22],       # OK to pit (yellow)
                'risky_window': [23, 24, 25],        # Risky (red)
                'danger_window': [26, 27, 28, ...],  # DANGER (past cliff)
                'lap_details': [PitWindowLap, ...],  # Full details for each lap
                'optimal_lap': 20,                   # AI's single best recommendation
                'never_pit': {...}                   # What if user never pits?
            }
        """

        # Calculate when tire hits cliff
        max_laps = self.tire_model.COMPOUND_WEAR_RATES[current_compound]['max_laps']
        cliff_lap = current_lap + (max_laps - current_tire_age)

        # Analyze pit options for next 15 laps (or until race end)
        window_size = min(15, laps_remaining)
        lap_details = []

        best_lap = None
        best_impact = float('inf')

        for offset in range(window_size + 1):
            pit_lap = current_lap + offset
            tire_age_at_pit = current_tire_age + offset

            # Calculate race impact if pitting this lap
            impact = self._calculate_pit_impact_at_lap(
                pit_lap=pit_lap,
                tire_age_at_pit=tire_age_at_pit,
                current_compound=current_compound,
                laps_remaining=laps_remaining - offset
            )

            # Determine recommendation level based on TIRE WEAR PERCENTAGE
            tire_age_pct = tire_age_at_pit / max_laps

            if tire_age_pct < 0.70:
                # Too early - not in optimal window yet (less than 70% worn)
                rec = 'ACCEPTABLE'
                color = 'yellow'
                reason = f'Early pit - tire only {tire_age_pct:.0%} worn'
            elif tire_age_pct <= 0.85:
                # OPTIMAL window - 70-85% tire wear (GREEN ZONE!)
                rec = 'HIGHLY_RECOMMENDED' if impact['race_time_impact'] == best_impact else 'RECOMMENDED'
                color = 'green'
                reason = f'Optimal window - tire at {tire_age_pct:.0%} (70-85% is ideal)'
            elif tire_age_pct <= 0.95:
                # Risky - 85-95% tire wear (approaching cliff)
                rec = 'RISKY'
                color = 'red'
                reason = f'Late pit - tire at {tire_age_pct:.0%} (risky, near cliff)'
            else:
                # DANGER - 95%+ tire wear (at/past cliff!)
                rec = 'DANGER'
                color = 'red'
                reason = f'DANGER - tire at {tire_age_pct:.0%} (past cliff!)'

            lap_details.append(PitWindowLap(
                lap_number=pit_lap,
                tire_age_at_lap=tire_age_at_pit,
                tire_compound_before=current_compound,
                best_compound=impact['best_compound'],
                race_time_impact=impact['race_time_impact'],
                recommendation=rec,
                reasoning=reason,
                color=color
            ))

            # Track best lap
            if impact['race_time_impact'] < best_impact:
                best_impact = impact['race_time_impact']
                best_lap = pit_lap

        # Categorize laps by recommendation
        recommended = [lap for lap in lap_details if lap.recommendation in ['HIGHLY_RECOMMENDED', 'RECOMMENDED']]
        acceptable = [lap for lap in lap_details if lap.recommendation == 'ACCEPTABLE']
        risky = [lap for lap in lap_details if lap.recommendation == 'RISKY']
        danger = [lap for lap in lap_details if lap.recommendation == 'DANGER']

        # Choose optimal lap as MIDDLE of green zone (not first green lap!)
        # This is the sweet spot: 77-78% tire wear
        if recommended:
            # Pick the middle lap of the green zone
            optimal_lap = recommended[len(recommended) // 2].lap_number
            optimal_compound = recommended[len(recommended) // 2].best_compound
        elif acceptable:
            # If no green zone, pick last acceptable lap (closest to 70%)
            optimal_lap = acceptable[-1].lap_number
            optimal_compound = acceptable[-1].best_compound
        else:
            # Fallback to best_lap
            optimal_lap = best_lap
            optimal_compound = next(lap.best_compound for lap in lap_details if lap.lap_number == best_lap)

        # Calculate "never pit" scenario
        never_pit_impact = self._calculate_never_pit_impact(
            current_lap=current_lap,
            current_tire_age=current_tire_age,
            current_compound=current_compound,
            laps_remaining=laps_remaining
        )

        return {
            'current_state': {
                'lap': current_lap,
                'tire_age': current_tire_age,
                'compound': current_compound,
                'cliff_lap': cliff_lap,
                'laps_to_cliff': cliff_lap - current_lap
            },
            'recommended_window': [lap.lap_number for lap in recommended],
            'acceptable_window': [lap.lap_number for lap in acceptable],
            'risky_window': [lap.lap_number for lap in risky],
            'danger_window': [lap.lap_number for lap in danger],
            'lap_details': lap_details,
            'optimal_lap': optimal_lap,
            'optimal_compound': optimal_compound,
            'optimal_impact': best_impact,
            'never_pit': never_pit_impact
        }

    def _calculate_pit_impact_at_lap(self, pit_lap: int, tire_age_at_pit: int,
                                     current_compound: str, laps_remaining: int) -> Dict:
        """Calculate race time impact if pitting at this specific lap"""

        # STRATEGY: Use HARD if enough laps remaining for one-stop
        # HARD max: 60 laps, so if >35 laps left, use HARD (can go to end)
        # Otherwise use MEDIUM for shorter stints

        if laps_remaining > 35:
            # Long stint - HARD is best (one-stop strategy)
            return {'race_time_impact': 25.0, 'best_compound': 'HARD'}
        elif laps_remaining > 15:
            # Medium stint - MEDIUM is good
            return {'race_time_impact': 25.0, 'best_compound': 'MEDIUM'}
        else:
            # Short stint to end - SOFT for speed
            return {'race_time_impact': 25.0, 'best_compound': 'SOFT'}

    def _simulate_pit_strategy(self, pit_lap: int, tire_age_at_pit: int,
                               current_compound: str, new_compound: str, laps_remaining: int) -> float:
        """Simulate full race if pitting this lap for this compound"""
        # Simplified - in real implementation, use tire model to calculate
        # For now, return mock data based on tire degradation

        # Time on current tires until pit
        # Time for pit stop (25s)
        # Time on new tires until end

        base_impact = 25.0  # Pit stop time

        # Add degradation penalty if past cliff
        max_laps = self.tire_model.COMPOUND_WEAR_RATES[current_compound]['max_laps']
        if tire_age_at_pit > max_laps:
            laps_over = tire_age_at_pit - max_laps
            base_impact += laps_over * 10  # 10s penalty per lap over cliff

        return base_impact

    def _calculate_never_pit_impact(self, current_lap: int, current_tire_age: int,
                                    current_compound: str, laps_remaining: int) -> Dict:
        """Calculate what happens if user NEVER pits for rest of race"""

        max_laps = self.tire_model.COMPOUND_WEAR_RATES[current_compound]['max_laps']
        final_tire_age = current_tire_age + laps_remaining

        if final_tire_age > max_laps:
            laps_over_cliff = final_tire_age - max_laps
            # Exponential penalty
            penalty = sum(10 * (1.5 ** i) for i in range(laps_over_cliff))

            return {
                'possible': False,
                'penalty': penalty,
                'final_tire_age': final_tire_age,
                'laps_over_cliff': laps_over_cliff,
                'warning': f'⛔ DISASTER - {laps_over_cliff} laps past cliff! +{penalty:.0f}s penalty'
            }
        else:
            return {
                'possible': True,
                'penalty': 0,
                'final_tire_age': final_tire_age,
                'laps_over_cliff': 0,
                'warning': None
            }


# Example usage for frontend
if __name__ == '__main__':
    from tire_model import TireDegradationModel

    tire_model = TireDegradationModel(total_laps=57, base_laptime=96.5, driving_style_multiplier=1.0)
    selector = PitWindowSelector(tire_model, total_laps=57)

    # User is on lap 18, tire age 18, SOFT tires
    window = selector.generate_pit_window(
        current_lap=18,
        current_tire_age=18,
        current_compound='SOFT',
        laps_remaining=39
    )

    print("\n🏎️  PIT WINDOW SELECTOR")
    print("="*70)
    print(f"\nCurrent state: Lap {window['current_state']['lap']}, " +
          f"{window['current_state']['compound']} tires, {window['current_state']['tire_age']} laps old")
    print(f"Tire cliff: Lap {window['current_state']['cliff_lap']} " +
          f"({window['current_state']['laps_to_cliff']} laps away)")

    print(f"\n🎯 AI OPTIMAL: Pit lap {window['optimal_lap']} " +
          f"for {window['optimal_compound']} tires ({window['optimal_impact']:+.1f}s)")

    print(f"\n🟢 RECOMMENDED WINDOW: Laps {window['recommended_window']}")
    print(f"🟡 ACCEPTABLE WINDOW:  Laps {window['acceptable_window']}")
    print(f"🔴 RISKY WINDOW:       Laps {window['risky_window']}")
    print(f"⛔ DANGER WINDOW:      Laps {window['danger_window']}")

    print("\n📊 LAP-BY-LAP BREAKDOWN:")
    for lap in window['lap_details'][:10]:  # Show first 10 laps
        emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}[lap.color]
        print(f"{emoji} Lap {lap.lap_number}: {lap.best_compound} tires ({lap.race_time_impact:+.1f}s) - {lap.reasoning}")

    if not window['never_pit']['possible']:
        print(f"\n{window['never_pit']['warning']}")
