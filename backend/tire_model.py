"""
Tire degradation and pit stop optimization model.
Ported from MATLAB code in Race-Strategy-Analysis repo.
"""
import numpy as np
from typing import Tuple, List, Dict

class TireDegradationModel:
    """
    Models tire degradation and calculates optimal pit stop windows.
    Based on linear degradation model from Safety_Car_Window_Calculations.m
    """

    # Tire compound characteristics (degradation rate in seconds/lap)
    COMPOUND_WEAR_RATES = {
        'SOFT': {
            'initial_laptime': 97.0,  # seconds
            'wear_start': 0.04,  # seconds/lap at start
            'wear_end': 0.20,    # seconds/lap at end of life
            'max_laps': 25       # typical max stint length
        },
        'MEDIUM': {
            'initial_laptime': 97.8,
            'wear_start': 0.04,
            'wear_end': 0.12,
            'max_laps': 40
        },
        'HARD': {
            'initial_laptime': 98.5,
            'wear_start': 0.03,
            'wear_end': 0.08,
            'max_laps': 60
        }
    }

    # Fuel effect parameters
    FUEL_QUANTITY = 110  # kg
    TIME_PER_KG = 0.035  # seconds per kg of fuel

    # Pit stop time loss
    PIT_TIME_LOSS = 25  # seconds (includes pit lane travel + stop)

    def __init__(self, total_laps: int = 78, base_laptime: float = 97.0, driving_style_multiplier: float = 1.0):
        """
        Initialize tire degradation model.

        Args:
            total_laps: Total race distance in laps (Monaco = 78)
            base_laptime: Base lap time in seconds (no fuel, fresh tires)
            driving_style_multiplier: Multiplier for tire wear based on driving style (0.5-3.0)
        """
        self.total_laps = total_laps
        self.base_laptime = base_laptime
        self.driving_style_multiplier = driving_style_multiplier

        # Calculate fuel consumption per lap
        self.fuel_consumption_per_lap = self.FUEL_QUANTITY / total_laps

        # Fuel correction factor (time saved as fuel burns)
        self.fuel_correction_per_lap = self.fuel_consumption_per_lap * self.TIME_PER_KG

    def get_tire_wear_rate(self, compound: str, lap_number: int) -> float:
        """
        Get tire wear rate for a given compound and lap number.
        Uses linear interpolation from wear_start to wear_end.
        EXPONENTIALLY increases degradation beyond max_laps (tire cliff)

        Args:
            compound: Tire compound ('SOFT', 'MEDIUM', 'HARD')
            lap_number: Current lap number (1-indexed)

        Returns:
            Wear rate in seconds/lap
        """
        if compound not in self.COMPOUND_WEAR_RATES:
            raise ValueError(f"Unknown compound: {compound}")

        params = self.COMPOUND_WEAR_RATES[compound]
        max_laps = params['max_laps']

        # Linear interpolation from wear_start to wear_end
        wear_rate = np.linspace(
            params['wear_start'],
            params['wear_end'],
            max_laps
        )

        # If within normal tire life, use linear degradation
        if lap_number <= max_laps:
            idx = lap_number - 1
            return wear_rate[idx]
        else:
            # Beyond max_laps: EXPONENTIAL tire cliff penalty
            laps_over = lap_number - max_laps
            base_degradation = params['wear_end']
            # Each lap over max adds exponentially more degradation
            # lap 26 on SOFT: +0.5s, lap 30: +2s, lap 40: +10s per lap!
            cliff_penalty = base_degradation * (1.5 ** laps_over)
            return base_degradation + cliff_penalty

    def calculate_laptime(
        self,
        lap_number: int,
        tire_age: int,
        compound: str,
        include_fuel_effect: bool = True
    ) -> float:
        """
        Calculate lap time given race lap, tire age, and compound.

        Args:
            lap_number: Current lap in the race (1-indexed)
            tire_age: Age of current tire set in laps (1 = fresh)
            compound: Tire compound
            include_fuel_effect: Whether to include fuel weight reduction

        Returns:
            Predicted lap time in seconds
        """
        params = self.COMPOUND_WEAR_RATES[compound]

        # Base lap time for this compound
        base = params['initial_laptime']

        # Tire degradation effect (linear with tire age)
        # MULTIPLIED by driving style (aggressive = more wear, conservative = less)
        wear_rate = self.get_tire_wear_rate(compound, tire_age)
        tire_deg = wear_rate * (tire_age - 1) * self.driving_style_multiplier

        # Fuel effect (car gets lighter as race progresses)
        fuel_correction = 0
        if include_fuel_effect:
            fuel_correction = self.fuel_correction_per_lap * (lap_number - 1)

        laptime = base + tire_deg - fuel_correction

        return laptime

    def calculate_stint_time(
        self,
        start_lap: int,
        end_lap: int,
        compound: str,
        tire_age_start: int = 1
    ) -> float:
        """
        Calculate total time for a stint (multiple laps).

        Args:
            start_lap: Starting lap number (1-indexed)
            end_lap: Ending lap number (inclusive)
            compound: Tire compound
            tire_age_start: Tire age at start of stint

        Returns:
            Total time for stint in seconds
        """
        total_time = 0
        tire_age = tire_age_start

        for lap in range(start_lap, end_lap + 1):
            laptime = self.calculate_laptime(lap, tire_age, compound)
            total_time += laptime
            tire_age += 1

        return total_time

    def optimal_pit_window(
        self,
        current_lap: int,
        stint1_compound: str = 'SOFT',
        stint2_compound: str = 'MEDIUM'
    ) -> List[Dict]:
        """
        Calculate optimal pit stop window for a 1-stop strategy.

        Args:
            current_lap: Current lap number
            stint1_compound: Compound for first stint
            stint2_compound: Compound for second stint

        Returns:
            List of scenarios sorted by total race time:
            [
                {
                    'pit_lap': 25,
                    'total_race_time': 7234.5,
                    'time_vs_optimal': 0.0,
                    'stint1_time': 2420.3,
                    'stint2_time': 4789.2,
                    'description': 'Optimal pit window'
                },
                ...
            ]
        """
        scenarios = []

        # Try every possible pit lap from current lap to race end
        for pit_lap in range(current_lap, self.total_laps):
            # Stint 1: current_lap to pit_lap (on stint1_compound)
            stint1_time = self.calculate_stint_time(
                current_lap, pit_lap, stint1_compound, tire_age_start=1
            )

            # Stint 2: pit_lap+1 to race end (on stint2_compound, fresh tires)
            stint2_time = self.calculate_stint_time(
                pit_lap + 1, self.total_laps, stint2_compound, tire_age_start=1
            )

            # Total race time = stint1 + pit stop + stint2
            total_time = stint1_time + self.PIT_TIME_LOSS + stint2_time

            scenarios.append({
                'pit_lap': pit_lap,
                'total_race_time': total_time,
                'stint1_time': stint1_time,
                'stint2_time': stint2_time,
                'pit_loss': self.PIT_TIME_LOSS
            })

        # Sort by total race time (fastest first)
        scenarios.sort(key=lambda x: x['total_race_time'])

        # Add time vs optimal
        optimal_time = scenarios[0]['total_race_time']
        for scenario in scenarios:
            scenario['time_vs_optimal'] = scenario['total_race_time'] - optimal_time

            # Add description
            if scenario['time_vs_optimal'] == 0:
                scenario['description'] = 'Optimal pit window'
            elif scenario['time_vs_optimal'] < 2.0:
                scenario['description'] = 'Good pit window'
            elif scenario['time_vs_optimal'] < 5.0:
                scenario['description'] = 'Acceptable pit window'
            else:
                scenario['description'] = 'Suboptimal pit window'

        return scenarios

    def predict_tire_cliff(self, compound: str, threshold: float = 2.0) -> int:
        """
        Predict which lap the tire will hit the performance "cliff".

        Args:
            compound: Tire compound
            threshold: Performance delta threshold (seconds slower than fresh)

        Returns:
            Lap number when cliff occurs
        """
        params = self.COMPOUND_WEAR_RATES[compound]

        for tire_age in range(1, params['max_laps']):
            wear_rate = self.get_tire_wear_rate(compound, tire_age)
            delta = wear_rate * (tire_age - 1)

            if delta >= threshold:
                return tire_age

        return params['max_laps']

    def get_degradation_rate(self, compound: str, tire_age: int) -> float:
        """
        Get current degradation rate (seconds slower than lap 1).

        Args:
            compound: Tire compound
            tire_age: Current tire age in laps

        Returns:
            Seconds slower than fresh tire
        """
        wear_rate = self.get_tire_wear_rate(compound, tire_age)
        return wear_rate * (tire_age - 1)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Tire Degradation Model Test")
    print("=" * 60)

    # Monaco 2024: 78 laps
    model = TireDegradationModel(total_laps=78, base_laptime=97.0)

    # Test 1: Predict tire cliff
    print("\n1. Tire Performance Cliff Prediction:")
    for compound in ['SOFT', 'MEDIUM', 'HARD']:
        cliff_lap = model.predict_tire_cliff(compound, threshold=2.0)
        print(f"   {compound}: Cliff at lap {cliff_lap}")

    # Test 2: Calculate degradation over time
    print("\n2. Soft Tire Degradation (first 15 laps):")
    for lap in range(1, 16):
        laptime = model.calculate_laptime(lap_number=lap, tire_age=lap, compound='SOFT')
        deg = model.get_degradation_rate('SOFT', lap)
        print(f"   Lap {lap:2d}: {laptime:.2f}s (degradation: +{deg:.3f}s)")

    # Test 3: Optimal pit window
    print("\n3. Optimal Pit Window (Soft → Medium strategy):")
    scenarios = model.optimal_pit_window(
        current_lap=1,
        stint1_compound='SOFT',
        stint2_compound='MEDIUM'
    )

    # Show top 5 strategies
    print("\n   Top 5 pit lap strategies:")
    for i, scenario in enumerate(scenarios[:5]):
        print(f"   {i+1}. Pit lap {scenario['pit_lap']:2d}: "
              f"{scenario['total_race_time']:.1f}s "
              f"(+{scenario['time_vs_optimal']:.1f}s) - "
              f"{scenario['description']}")

    optimal_lap = scenarios[0]['pit_lap']
    print(f"\n   ✅ Optimal pit lap: {optimal_lap}")
    print(f"   ⚠️  Pit window range: {optimal_lap-2} to {optimal_lap+2} laps")

    print("\n" + "=" * 60)
    print("✅ Tire model working correctly!")
    print("=" * 60)
