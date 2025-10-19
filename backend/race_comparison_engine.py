"""
Race Comparison Engine - Simulates AI strategy vs baseline in real-time
Calculates lap-by-lap performance for visual comparison
"""

import os
from typing import Dict, List
from dotenv import load_dotenv
from supabase import create_client, Client
from tire_model import TireDegradationModel

load_dotenv()

class RaceComparisonEngine:
    """
    Simulates two parallel race strategies:
    1. AI Strategy - follows coordinator recommendations (pits optimally)
    2. Baseline - no pit stop strategy (stays out or pits randomly)
    """

    def __init__(self, race_id: str = 'monaco_2024', driver: str = 'LEC'):
        self.race_id = race_id
        self.driver = driver
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        self.tire_model = TireDegradationModel()

        # Track state for both strategies
        self.ai_state = {
            'cumulative_time': 0.0,
            'current_compound': 'HARD',
            'tire_age': 0,
            'has_pitted': False,
            'pit_lap': None,
            'laps_completed': []
        }

        self.baseline_state = {
            'cumulative_time': 0.0,
            'current_compound': 'HARD',
            'tire_age': 0,
            'has_pitted': False,
            'pit_lap': None,
            'laps_completed': []
        }

    def get_ai_recommendation(self, current_lap: int) -> Dict:
        """Get AI coordinator recommendation for this lap"""
        try:
            response = self.supabase.table('agent_recommendations').select('*').eq(
                'race_id', self.race_id
            ).eq('lap_number', current_lap).limit(1).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching AI recommendation: {e}")
            return None

    def calculate_lap_time(self, compound: str, tire_age: int, base_lap_time: float = 78.0) -> float:
        """
        Calculate lap time based on tire compound and age
        Uses tire degradation model

        Args:
            compound: Tire compound (SOFT, MEDIUM, HARD)
            tire_age: Number of laps on current tires
            base_lap_time: Clean lap time in seconds

        Returns:
            Lap time in seconds
        """
        # Get degradation rate from tire model
        degradation = self.tire_model.calculate_degradation(compound, tire_age)

        # Lap time increases with degradation
        # degradation is in seconds per lap, cumulative
        lap_time = base_lap_time + degradation

        return lap_time

    def should_ai_pit(self, current_lap: int, recommendation: Dict) -> bool:
        """Determine if AI strategy should pit this lap"""
        if not recommendation:
            return False

        rec_type = recommendation.get('recommendation_type', '')

        # Pit if recommendation is PIT_NOW or PIT_SOON and we're in window
        if rec_type == 'PIT_NOW':
            return True
        elif rec_type == 'PIT_SOON':
            # Check if we're within 2 laps of optimal
            return current_lap % 5 == 0  # Simplified: pit every 5 laps if PIT_SOON

        return False

    def execute_pit_stop(self, strategy_state: Dict, current_lap: int, new_compound: str = 'MEDIUM'):
        """Execute a pit stop for a strategy"""
        PIT_TIME_LOSS = 25.0  # seconds

        strategy_state['cumulative_time'] += PIT_TIME_LOSS
        strategy_state['current_compound'] = new_compound
        strategy_state['tire_age'] = 0  # Reset tire age
        strategy_state['has_pitted'] = True
        strategy_state['pit_lap'] = current_lap

    def simulate_lap(self, current_lap: int, total_laps: int = 78) -> Dict:
        """
        Simulate one lap for both strategies

        Returns:
            Comparison data for this lap
        """
        # Get AI recommendation
        ai_rec = self.get_ai_recommendation(current_lap)

        # Check if AI should pit
        if self.should_ai_pit(current_lap, ai_rec) and not self.ai_state['has_pitted']:
            self.execute_pit_stop(self.ai_state, current_lap, 'MEDIUM')

        # Baseline never pits (or pits at fixed lap like 50)
        # For Monaco demo: baseline stays out (track position > tire performance)

        # Calculate lap times for both strategies
        ai_lap_time = self.calculate_lap_time(
            self.ai_state['current_compound'],
            self.ai_state['tire_age']
        )

        baseline_lap_time = self.calculate_lap_time(
            self.baseline_state['current_compound'],
            self.baseline_state['tire_age']
        )

        # Update cumulative times
        self.ai_state['cumulative_time'] += ai_lap_time
        self.baseline_state['cumulative_time'] += baseline_lap_time

        # Increment tire ages
        self.ai_state['tire_age'] += 1
        self.baseline_state['tire_age'] += 1

        # Track completed laps
        self.ai_state['laps_completed'].append(current_lap)
        self.baseline_state['laps_completed'].append(current_lap)

        # Return comparison data for frontend
        return {
            'current_lap': current_lap,
            'total_laps': total_laps,
            'ai_strategy': {
                'cumulative_time': self.ai_state['cumulative_time'],
                'current_compound': self.ai_state['current_compound'],
                'tire_age': self.ai_state['tire_age'],
                'has_pitted': self.ai_state['has_pitted'],
                'pit_lap': self.ai_state['pit_lap'],
                'last_lap_time': ai_lap_time
            },
            'baseline': {
                'cumulative_time': self.baseline_state['cumulative_time'],
                'current_compound': self.baseline_state['current_compound'],
                'tire_age': self.baseline_state['tire_age'],
                'has_pitted': self.baseline_state['has_pitted'],
                'pit_lap': self.baseline_state['pit_lap'],
                'last_lap_time': baseline_lap_time
            },
            'time_difference': self.ai_state['cumulative_time'] - self.baseline_state['cumulative_time']
        }

    def save_comparison_to_db(self, comparison_data: Dict):
        """Save comparison snapshot to database for frontend polling"""
        try:
            self.supabase.table('race_comparison').upsert({
                'race_id': self.race_id,
                'driver_name': self.driver,
                'lap_number': comparison_data['current_lap'],
                'ai_cumulative_time': comparison_data['ai_strategy']['cumulative_time'],
                'ai_tire_compound': comparison_data['ai_strategy']['current_compound'],
                'ai_tire_age': comparison_data['ai_strategy']['tire_age'],
                'ai_has_pitted': comparison_data['ai_strategy']['has_pitted'],
                'baseline_cumulative_time': comparison_data['baseline']['cumulative_time'],
                'baseline_tire_compound': comparison_data['baseline']['current_compound'],
                'baseline_tire_age': comparison_data['baseline']['tire_age'],
                'baseline_has_pitted': comparison_data['baseline']['has_pitted'],
                'time_difference': comparison_data['time_difference']
            }, on_conflict='race_id,driver_name,lap_number').execute()
        except Exception as e:
            print(f"⚠️  Error saving comparison to DB: {e}")
            print("   (This is fine if race_comparison table doesn't exist yet)")

    def get_latest_comparison(self) -> Dict:
        """Get latest comparison data from database"""
        try:
            response = self.supabase.table('race_comparison').select('*').eq(
                'race_id', self.race_id
            ).eq('driver_name', self.driver).order('lap_number', desc=True).limit(1).execute()

            if response.data and len(response.data) > 0:
                data = response.data[0]
                return {
                    'current_lap': data['lap_number'],
                    'total_laps': 78,
                    'ai_strategy': {
                        'cumulative_time': data['ai_cumulative_time'],
                        'current_compound': data['ai_tire_compound'],
                        'tire_age': data['ai_tire_age'],
                        'has_pitted': data['ai_has_pitted'],
                        'pit_lap': data.get('ai_pit_lap')
                    },
                    'baseline': {
                        'cumulative_time': data['baseline_cumulative_time'],
                        'current_compound': data['baseline_tire_compound'],
                        'tire_age': data['baseline_tire_age'],
                        'has_pitted': data['baseline_has_pitted'],
                        'pit_lap': data.get('baseline_pit_lap')
                    },
                    'time_difference': data['time_difference']
                }
            return None
        except Exception as e:
            print(f"Error fetching comparison: {e}")
            return None


if __name__ == '__main__':
    """Test the comparison engine"""
    engine = RaceComparisonEngine()

    print("🏁 Testing Race Comparison Engine")
    print("="*60)

    # Simulate laps 1-70
    for lap in range(1, 71):
        comparison = engine.simulate_lap(lap, total_laps=78)

        if lap % 10 == 0:  # Print every 10 laps
            print(f"\nLap {lap}:")
            print(f"  AI Strategy: {comparison['ai_strategy']['cumulative_time']:.1f}s "
                  f"({comparison['ai_strategy']['current_compound']}, age {comparison['ai_strategy']['tire_age']})")
            print(f"  Baseline: {comparison['baseline']['cumulative_time']:.1f}s "
                  f"({comparison['baseline']['current_compound']}, age {comparison['baseline']['tire_age']})")
            print(f"  Difference: {comparison['time_difference']:.1f}s")

            if comparison['ai_strategy']['has_pitted']:
                print(f"  🔧 AI pitted on lap {comparison['ai_strategy']['pit_lap']}")

        # Save to database
        engine.save_comparison_to_db(comparison)

    print("\n" + "="*60)
    print("✅ Comparison simulation complete!")
