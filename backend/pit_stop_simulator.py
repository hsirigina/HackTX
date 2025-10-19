"""
Pit Stop Simulator - For hackathon demo
Allows manual pit stop execution to test strategy recommendations
"""

class PitStopSimulator:
    """
    Simulates pit stop effects on race data
    """

    PIT_TIME_LOSS = 25.0  # seconds (pit lane + stop time)

    def __init__(self, supabase_client, race_id: str):
        """
        Initialize pit stop simulator

        Args:
            supabase_client: Supabase client for data updates
            race_id: Race identifier
        """
        self.supabase = supabase_client
        self.race_id = race_id
        self.pit_stops_executed = []

    def execute_pit_stop(
        self,
        current_lap: int,
        driver_number: int,
        driver_name: str,
        new_compound: str = 'MEDIUM'
    ) -> dict:
        """
        Execute a pit stop for demo purposes

        Args:
            current_lap: Lap when pit stop occurs
            driver_number: Driver number
            driver_name: Driver name
            new_compound: Tire compound to fit

        Returns:
            dict with pit stop details
        """
        print(f"\n{'='*60}")
        print(f"🔧 SIMULATING PIT STOP - Lap {current_lap}")
        print(f"{'='*60}")
        print(f"Driver: {driver_name} (#{driver_number})")
        print(f"New compound: {new_compound}")
        print(f"Time loss: {self.PIT_TIME_LOSS}s")

        # Get current tire compound from tire_data
        old_compound = 'HARD'  # Default
        try:
            tire_response = self.supabase.table('tire_data').select('compound').eq(
                'race_id', self.race_id
            ).eq('driver_name', driver_name).order('lap_number', desc=True).limit(1).execute()

            if tire_response.data and len(tire_response.data) > 0:
                old_compound = tire_response.data[0]['compound']
        except Exception as e:
            print(f"⚠️  Could not fetch current tire compound: {e}")

        print(f"Tire change: {old_compound} → {new_compound}")

        # Record pit stop
        pit_stop = {
            'lap': current_lap,
            'driver': driver_name,
            'old_compound': old_compound,
            'new_compound': new_compound,
            'time_loss': self.PIT_TIME_LOSS,
            'tire_age_reset': True
        }
        self.pit_stops_executed.append(pit_stop)

        # Insert pit stop record into database
        try:
            self.supabase.table('pit_stops').insert({
                'race_id': self.race_id,
                'driver_number': driver_number,
                'driver_name': driver_name,
                'lap_number': current_lap,
                'pit_duration_seconds': self.PIT_TIME_LOSS,
                'old_compound': old_compound,
                'new_compound': new_compound
            }).execute()
            print(f"✅ Pit stop recorded in database")
        except Exception as e:
            print(f"⚠️  Error recording pit stop: {e}")

        # Update tire data for subsequent laps (would need to intercept race replay)
        # For demo: this would modify the tire_data being saved

        print(f"{'='*60}\n")

        return pit_stop

    def get_pit_stop_summary(self) -> dict:
        """Get summary of all executed pit stops"""
        return {
            'total_stops': len(self.pit_stops_executed),
            'total_time_loss': sum(p['time_loss'] for p in self.pit_stops_executed),
            'stops': self.pit_stops_executed
        }

    def calculate_strategy_impact(
        self,
        baseline_time: float,
        tire_deg_savings: float,
        pit_time_loss: float
    ) -> dict:
        """
        Calculate impact of pit stop strategy vs no-stop

        Args:
            baseline_time: Total race time with no pit
            tire_deg_savings: Time saved by having fresher tires
            pit_time_loss: Time lost in pit stops

        Returns:
            Comparison data
        """
        new_time = baseline_time - tire_deg_savings + pit_time_loss
        delta = new_time - baseline_time

        return {
            'no_pit_strategy': {
                'total_time': baseline_time,
                'tire_degradation': 0,
                'pit_time': 0
            },
            'pit_strategy': {
                'total_time': new_time,
                'tire_degradation_saved': tire_deg_savings,
                'pit_time_lost': pit_time_loss
            },
            'delta': delta,
            'faster': 'pit_strategy' if delta < 0 else 'no_pit_strategy',
            'time_difference': abs(delta)
        }


if __name__ == "__main__":
    print("Pit Stop Simulator - Test")
    print("="*60)

    # Example: Monaco 2024 strategy comparison
    print("\nSCENARIO: Monaco 2024 - Lap 66 pit stop decision")
    print("-"*60)

    simulator = PitStopSimulator(None, 'monaco_2024_test')

    # Simulate strategy comparison
    comparison = simulator.calculate_strategy_impact(
        baseline_time=5400.0,  # 78 laps, no pit
        tire_deg_savings=15.0,  # Saved ~15s with fresher tires laps 66-78
        pit_time_loss=25.0      # One pit stop
    )

    print(f"\nNo-pit strategy: {comparison['no_pit_strategy']['total_time']:.1f}s")
    print(f"Pit strategy: {comparison['pit_strategy']['total_time']:.1f}s")
    print(f"\nResult: {comparison['faster']} is faster by {comparison['time_difference']:.1f}s")
    print("\nIn Monaco, track position > tire performance!")
    print("No pit was correct strategy.")
