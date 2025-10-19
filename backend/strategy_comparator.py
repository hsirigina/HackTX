"""
Strategy Comparator - Compare AI strategy vs actual race outcome
Perfect for hackathon demo to show AI value
"""

from tire_model import TireDegradationModel
from typing import List, Dict

class StrategyComparator:
    """
    Compares different pit stop strategies for the same race
    """

    def __init__(self, total_laps: int = 78):
        """Initialize with tire degradation model"""
        self.tire_model = TireDegradationModel(total_laps=total_laps)
        self.total_laps = total_laps

    def compare_strategies(
        self,
        start_lap: int,
        end_lap: int,
        current_tire_age: int,
        current_compound: str
    ) -> Dict:
        """
        Compare NO-PIT vs AI-RECOMMENDED pit strategy

        Args:
            start_lap: Current lap
            end_lap: Final lap
            current_tire_age: Current tire age in laps
            current_compound: Current tire compound

        Returns:
            Comparison data with projections
        """
        remaining_laps = end_lap - start_lap + 1

        # STRATEGY 1: No pit (stay out like real Monaco 2024)
        no_pit_time = self.tire_model.calculate_stint_time(
            start_lap=start_lap,
            end_lap=end_lap,
            compound=current_compound,
            tire_age_start=current_tire_age
        )

        # STRATEGY 2: Pit now (follow AI recommendation)
        pit_now_time = (
            25.0 +  # Pit stop time loss
            self.tire_model.calculate_stint_time(
                start_lap=start_lap,
                end_lap=end_lap,
                compound='MEDIUM',  # Fresh mediums
                tire_age_start=1  # Brand new tires
            )
        )

        # STRATEGY 3: Optimal pit window (what tire model suggests)
        scenarios = self.tire_model.optimal_pit_window(
            current_lap=start_lap,
            stint1_compound=current_compound,
            stint2_compound='MEDIUM'
        )

        optimal_scenario = scenarios[0]
        optimal_pit_lap = optimal_scenario['pit_lap']
        optimal_time = optimal_scenario['total_race_time']

        # Calculate time differences
        delta_pit_now = pit_now_time - no_pit_time
        delta_optimal = optimal_time - no_pit_time

        return {
            'strategies': {
                'no_pit': {
                    'description': 'Stay out entire race',
                    'total_time': no_pit_time,
                    'tire_compound': current_compound,
                    'final_tire_age': current_tire_age + remaining_laps,
                    'pit_stops': 0,
                    'delta_vs_no_pit': 0.0
                },
                'pit_now': {
                    'description': f'Pit immediately (lap {start_lap})',
                    'total_time': pit_now_time,
                    'tire_compound': 'MEDIUM',
                    'final_tire_age': remaining_laps,
                    'pit_stops': 1,
                    'delta_vs_no_pit': delta_pit_now
                },
                'optimal': {
                    'description': f'Pit on optimal lap {optimal_pit_lap}',
                    'total_time': optimal_time,
                    'tire_compound': 'MEDIUM',
                    'final_tire_age': end_lap - optimal_pit_lap,
                    'pit_stops': 1,
                    'pit_lap': optimal_pit_lap,
                    'delta_vs_no_pit': delta_optimal
                }
            },
            'recommendation': self._get_recommendation(delta_pit_now, delta_optimal),
            'context': {
                'current_lap': start_lap,
                'laps_remaining': remaining_laps,
                'current_tire_age': current_tire_age
            }
        }

    def _get_recommendation(self, delta_pit_now: float, delta_optimal: float) -> str:
        """Generate recommendation based on time deltas"""
        if delta_optimal < -2.0:
            return f"✅ STRATEGY ADVANTAGE: Pitting saves {abs(delta_optimal):.1f}s - Follow AI recommendation!"
        elif delta_optimal > 2.0:
            return f"❌ STRATEGY DISADVANTAGE: Staying out faster by {delta_optimal:.1f}s - Track position is key"
        else:
            return f"⚖️ MARGINAL DIFFERENCE: Strategies within {abs(delta_optimal):.1f}s - Driver preference"

    def print_comparison(self, comparison: Dict):
        """Pretty print strategy comparison for terminal"""
        print("\n" + "="*70)
        print("🏁 STRATEGY COMPARISON - What if we followed AI recommendations?")
        print("="*70)

        for name, strat in comparison['strategies'].items():
            symbol = "⭐" if name == 'optimal' else "📊"
            delta_str = f"({strat['delta_vs_no_pit']:+.1f}s)" if strat['delta_vs_no_pit'] != 0 else "(baseline)"

            print(f"\n{symbol} {name.upper().replace('_', ' ')}: {delta_str}")
            print(f"   {strat['description']}")
            print(f"   Total time: {strat['total_time']:.1f}s")
            print(f"   Final tire age: {strat['final_tire_age']} laps on {strat['tire_compound']}")

        print("\n" + "-"*70)
        print(comparison['recommendation'])
        print("="*70 + "\n")


if __name__ == "__main__":
    print("Strategy Comparator - Monaco 2024 Example")
    print("="*70)

    comparator = StrategyComparator(total_laps=78)

    # Simulate: We're at lap 64, tire age 63, HARD compound
    print("\nSCENARIO: Lap 64, HARD tires (63 laps old)")
    print("AI Recommendation: PIT_SOON (window laps 65-67)")
    print("\nWhat would happen if we follow vs ignore AI?\n")

    comparison = comparator.compare_strategies(
        start_lap=64,
        end_lap=78,
        current_tire_age=63,
        current_compound='HARD'
    )

    comparator.print_comparison(comparison)

    print("\nCONCLUSION:")
    print("Monaco is unique - tire degradation is low, track position is king.")
    print("In this case, staying out was correct (as real race showed).")
    print("\nBUT: On other tracks (Silverstone, Spain), pitting would be faster!")
    print("="*70)
