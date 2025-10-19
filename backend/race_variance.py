"""
Race Variance System - Adds realistic randomness to make races winnable
Includes: luck events, traffic, safety cars, track evolution
"""

import random
from typing import Dict, List


class RaceVariance:
    """
    Adds realistic variance to race outcomes so perfect execution can win
    - Luck events (good/bad)
    - Traffic effects
    - Safety car chances
    - Track evolution
    """

    def __init__(self, total_laps: int, luck_factor: float = 0.5):
        """
        Args:
            total_laps: Total race laps
            luck_factor: 0.0-1.0, how much luck affects outcome
                        0.0 = no luck (deterministic)
                        0.5 = moderate luck (default)
                        1.0 = high variance (very random)
        """
        self.total_laps = total_laps
        self.luck_factor = luck_factor
        self.events = []  # Track all events for summary

    def get_lap_variance(self, lap: int, position: int) -> Dict:
        """
        Calculate variance for this lap

        Returns:
            {
                'time_delta': float,  # +/- seconds for this lap
                'event': str,         # Description of what happened
                'type': str           # 'luck', 'traffic', 'safety_car', etc.
            }
        """
        # Base variance: small random fluctuation every lap
        base_variance = random.gauss(0, 0.1) * self.luck_factor  # ±0.1s typical

        # Check for special events
        event = self._check_for_event(lap, position)

        if event:
            self.events.append(event)
            return event
        else:
            return {
                'time_delta': base_variance,
                'event': None,
                'type': 'normal'
            }

    def _check_for_event(self, lap: int, position: int) -> Dict:
        """Check if a special event happens this lap"""

        # SAFETY CAR (5% chance per lap, more likely mid-race)
        if 10 < lap < 50 and random.random() < 0.05 * self.luck_factor:
            # Safety car bunches field - reset gaps
            time_delta = random.uniform(-15, -5)  # Gain 5-15s (catch up to leader)
            return {
                'time_delta': time_delta,
                'event': f'🟡 SAFETY CAR - Lap {lap}! Field bunched up',
                'type': 'safety_car'
            }

        # TRAFFIC LUCK (varies by position)
        if position > 5 and random.random() < 0.03:
            # Lose time lapping backmarkers
            time_delta = random.uniform(0.5, 2.0)
            return {
                'time_delta': time_delta,
                'event': f'🚦 Traffic - Lost {time_delta:.1f}s lapping slower cars',
                'type': 'traffic_bad'
            }
        elif position <= 3 and random.random() < 0.02:
            # Clear track, gain time
            time_delta = random.uniform(-0.5, -0.2)
            return {
                'time_delta': time_delta,
                'event': f'✨ Clear track - Gained {abs(time_delta):.1f}s',
                'type': 'traffic_good'
            }

        # GOOD LUCK EVENTS (2% chance)
        if random.random() < 0.02 * self.luck_factor:
            luck_type = random.choice([
                ('Perfect exit from Turn 1', random.uniform(-0.3, -0.1)),
                ('Slipstream down main straight', random.uniform(-0.4, -0.2)),
                ('Nailed the final sector', random.uniform(-0.5, -0.2)),
                ('DRS overtake, gained momentum', random.uniform(-0.6, -0.3))
            ])
            return {
                'time_delta': luck_type[1],
                'event': f'🍀 {luck_type[0]}',
                'type': 'luck_good'
            }

        # BAD LUCK EVENTS (2% chance)
        if random.random() < 0.02 * self.luck_factor:
            bad_type = random.choice([
                ('Locked up into Turn 1', random.uniform(0.3, 0.8)),
                ('Ran wide at Turn 4', random.uniform(0.2, 0.5)),
                ('Defended position, lost momentum', random.uniform(0.3, 0.6)),
                ('Yellow flags in sector 3', random.uniform(0.4, 1.0))
            ])
            return {
                'time_delta': bad_type[1],
                'event': f'⚠️  {bad_type[0]}',
                'type': 'luck_bad'
            }

        return None

    def get_strategy_bonus(self, user_pits: int, user_compounds: List[str],
                          comparison_pits: int) -> float:
        """
        Bonus/penalty for strategy execution vs VER

        Returns:
            time_delta: negative = faster, positive = slower
        """
        bonus = 0.0

        # One-stop vs two-stop advantage
        if user_pits == 1 and comparison_pits == 2:
            # Saved a pit stop!
            bonus -= 20.0
        elif user_pits == 2 and comparison_pits == 1:
            # Extra pit stop
            bonus += 15.0

        # Tire choice bonus (HARD for long stints is smart)
        if 'HARD' in user_compounds and user_pits == 1:
            bonus -= 3.0  # Smart one-stop strategy

        return bonus

    def get_final_variance_summary(self) -> str:
        """Get summary of all variance events for display"""
        if not self.events:
            return "No major events - clean race!"

        summary = []
        total_gain = 0
        total_loss = 0

        for event in self.events:
            if event['time_delta'] < 0:
                total_gain += abs(event['time_delta'])
            else:
                total_loss += event['time_delta']
            summary.append(event['event'])

        result = "\n   ".join(summary)
        net = total_gain - total_loss

        if net > 0:
            result += f"\n   📊 Net luck: GAINED {net:.1f}s"
        elif net < 0:
            result += f"\n   📊 Net luck: LOST {abs(net):.1f}s"
        else:
            result += f"\n   📊 Net luck: Neutral"

        return result


# Quick test
if __name__ == '__main__':
    print("Testing Race Variance System\n")

    variance = RaceVariance(total_laps=57, luck_factor=0.7)

    total_delta = 0
    events_count = 0

    for lap in range(1, 58):
        result = variance.get_lap_variance(lap, position=3)
        total_delta += result['time_delta']

        if result['event']:
            events_count += 1
            print(f"Lap {lap:2d}: {result['event']} ({result['time_delta']:+.1f}s)")

    print(f"\nTotal variance: {total_delta:+.1f}s over 57 laps")
    print(f"Events triggered: {events_count}")
    print(f"\nSummary:")
    print(variance.get_final_variance_summary())
