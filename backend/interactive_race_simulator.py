"""
Interactive Race Simulator - User plays as race engineer
Simulates lap-by-lap race, pauses for user decisions, compares final time to actual winner
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from tire_model import TireDegradationModel
from driving_style import DrivingStyle, DrivingStyleManager
from data_agents import CompetitorAgent
import fastf1


@dataclass
class RaceState:
    """Current state of user's simulated car"""
    current_lap: int
    position: int
    total_race_time: float  # Cumulative time in seconds

    # Tire state
    tire_compound: str
    tire_age: int

    # Driving state
    driving_style: DrivingStyle

    # Pit history
    pit_stops: List[Dict]  # [{'lap': 12, 'compound': 'MEDIUM', 'reason': 'Undercut VER'}]

    # Decision history
    decisions_made: List[Dict]


@dataclass
class DecisionOption:
    """A strategic option presented to the user"""
    option_id: int
    category: str  # 'PIT_STOP', 'DRIVING_STYLE', 'TACTIC'
    title: str
    description: str

    # Parameters for this option
    action: str  # 'PIT_NOW', 'STAY_OUT', 'SET_STYLE_AGGRESSIVE', etc.
    parameters: Dict  # {'compound': 'MEDIUM'} or {'style': 'AGGRESSIVE'}

    # Predictions
    predicted_lap_time_impact: float  # Expected lap time change
    predicted_race_time_impact: float  # Expected total race time change
    tire_wear_impact: float

    # AI reasoning
    reasoning: str
    pros: List[str]
    cons: List[str]

    # Recommendation strength
    ai_confidence: str  # 'HIGHLY_RECOMMENDED', 'RECOMMENDED', 'ALTERNATIVE'


class InteractiveRaceSimulator:
    """
    Simulates user's race lap-by-lap, generating strategic decisions at key moments
    Uses tire model + competitor analysis to create realistic options
    """

    def __init__(self, race_year: int, race_name: str, total_laps: int, comparison_driver: str = 'VER'):
        """
        Initialize race simulator

        Args:
            race_year: Year (e.g., 2024)
            race_name: Race name (e.g., 'Bahrain')
            total_laps: Total race laps (e.g., 57 for Bahrain)
            comparison_driver: Driver to compare against (default: Verstappen)
        """
        self.race_year = race_year
        self.race_name = race_name
        self.total_laps = total_laps
        self.comparison_driver = comparison_driver

        # Load actual race data for competitor positions
        print(f"📥 Loading {race_year} {race_name} race data...")
        self.session = fastf1.get_session(race_year, race_name, 'R')
        self.session.load(telemetry=False, weather=False, messages=False)

        # Get comparison driver's actual race
        self.comparison_laps = self.session.laps.pick_driver(comparison_driver)

        # Use SUM of lap times, not cumulative time (which includes formation lap + delays)
        self.comparison_laptimes = self.comparison_laps['LapTime'].dt.total_seconds()
        self.comparison_total_time = self.comparison_laptimes.sum()
        self.comparison_avg_laptime = self.comparison_laptimes.mean()

        print(f"   ✅ {comparison_driver} total race time: {self.comparison_total_time:.1f}s ({len(self.comparison_laptimes)} laps)")
        print(f"   ✅ {comparison_driver} average lap time: {self.comparison_avg_laptime:.2f}s")

        # Initialize race state (user starts on grid)
        self.state = None  # Will be set in start_race()

        # Decision points (laps where we'll pause for user input)
        self.decision_laps = self._calculate_decision_points()

        # Tire model and driving style
        self.tire_model = None  # Created when race starts with initial style
        self.style_manager = DrivingStyleManager(DrivingStyle.BALANCED)

        # Competitor tracking (we'll track our own simulated driver "USER")
        self.competitor_agent = CompetitorAgent(driver_name="USER")

    def start_race(self, starting_position: int = 3, starting_compound: str = 'SOFT') -> Dict:
        """
        Start the race simulation

        Args:
            starting_position: Grid position (default: P3)
            starting_compound: Starting tire compound

        Returns:
            Initial race state info
        """
        self.state = RaceState(
            current_lap=1,
            position=starting_position,
            total_race_time=0.0,
            tire_compound=starting_compound,
            tire_age=1,
            driving_style=DrivingStyle.BALANCED,
            pit_stops=[],
            decisions_made=[]
        )

        # Initialize tire model with current driving style
        # Use VER's actual average lap time as baseline for realism
        self.tire_model = TireDegradationModel(
            total_laps=self.total_laps,
            base_laptime=self.comparison_avg_laptime,
            driving_style_multiplier=self.style_manager.get_tire_wear_multiplier()
        )

        print(f"\n🏁 RACE START - {self.race_name} Grand Prix")
        print(f"   Grid Position: P{starting_position}")
        print(f"   Starting Tires: {starting_compound}")
        print(f"   Total Laps: {self.total_laps}")
        print(f"   Target: Beat {self.comparison_driver}'s time of {self.comparison_total_time:.1f}s\n")

        return {
            'race_name': self.race_name,
            'total_laps': self.total_laps,
            'starting_position': starting_position,
            'comparison_driver': self.comparison_driver,
            'comparison_time': self.comparison_total_time
        }

    def _calculate_decision_points(self) -> List[int]:
        """
        Calculate which laps to pause for user decisions
        Based on typical F1 strategy windows
        """
        decision_laps = []

        # Lap 1: Initial driving style choice
        decision_laps.append(1)

        # First pit window (laps 10-15)
        decision_laps.extend([10, 12, 15])

        # Mid-race tactics (laps 20-30)
        decision_laps.extend([20, 25, 30])

        # Second pit window (laps 33-38)
        decision_laps.extend([33, 35, 38])

        # Final stint decisions (laps 45-55)
        decision_laps.extend([45, 50, 55])

        return sorted(decision_laps)

    def simulate_lap(self, lap_number: int) -> Tuple[float, Dict]:
        """
        Simulate a single lap based on current state

        Args:
            lap_number: Current lap number

        Returns:
            (lap_time, lap_info)
        """
        # Calculate base lap time from tire model
        base_lap_time = self.tire_model.calculate_laptime(
            lap_number=lap_number,
            tire_age=self.state.tire_age,
            compound=self.state.tire_compound
        )

        # Apply driving style adjustment
        style_delta = self.style_manager.get_lap_time_adjustment()
        lap_time = base_lap_time + style_delta

        # Update tire age
        self.state.tire_age += 1

        # Update total race time
        self.state.total_race_time += lap_time

        return lap_time, {
            'lap': lap_number,
            'lap_time': lap_time,
            'tire_age': self.state.tire_age,
            'compound': self.state.tire_compound,
            'style': self.state.driving_style.value,
            'cumulative_time': self.state.total_race_time
        }

    def generate_decision_options(self, lap_number: int) -> List[DecisionOption]:
        """
        Generate 3 strategic options for user to choose from
        Uses tire model + competitor data

        Args:
            lap_number: Current lap number

        Returns:
            List of 3 DecisionOption objects
        """
        options = []

        # Get competitor context
        competitor_status = self._get_competitor_context(lap_number)

        # Determine decision type based on lap
        if lap_number == 1:
            # Initial driving style decision
            options = self._generate_driving_style_options(lap_number, competitor_status)

        elif lap_number in [10, 12, 15, 33, 35, 38]:
            # Pit stop windows
            options = self._generate_pit_stop_options(lap_number, competitor_status)

        elif lap_number in [20, 25, 30, 45, 50]:
            # Tactical decisions (driving style + push/conserve)
            options = self._generate_tactical_options(lap_number, competitor_status)

        elif lap_number == 55:
            # Final laps - attack or manage?
            options = self._generate_final_laps_options(lap_number, competitor_status)

        # Ensure we always return exactly 3 options
        return options[:3]

    def _get_competitor_context(self, lap_number: int) -> Dict:
        """
        Get competitor positions and tire data from actual race at this lap

        Returns:
            {
                'gap_ahead': 2.5,  # seconds
                'gap_behind': 5.0,
                'leader_tire_age': 12,
                'nearby_threats': [...],
                'nearby_opportunities': [...]
            }
        """
        # For now, return mock data - will integrate with actual FastF1 data
        # This would query the actual race lap times and positions

        return {
            'gap_ahead': 2.5,
            'gap_behind': 5.0,
            'leader': 'VER',
            'leader_tire_age': lap_number - 1,  # Simplified
            'p2_tire_age': lap_number - 1,
            'nearby_threats': [],
            'nearby_opportunities': []
        }

    def _generate_pit_stop_options(self, lap_number: int, context: Dict) -> List[DecisionOption]:
        """Generate pit stop vs stay out options"""
        options = []
        laps_remaining = self.total_laps - lap_number

        # Option 1: PIT NOW for MEDIUM tires
        pit_now_medium = self._calculate_pit_impact(lap_number, 'MEDIUM', laps_remaining)
        options.append(DecisionOption(
            option_id=1,
            category='PIT_STOP',
            title='Pit Now - Medium Tires',
            description=f'Box this lap for MEDIUM compound',
            action='PIT_NOW',
            parameters={'compound': 'MEDIUM'},
            predicted_lap_time_impact=-25.0,  # Pit loss
            predicted_race_time_impact=pit_now_medium['race_time_impact'],
            tire_wear_impact=0.0,  # Fresh tires
            reasoning=pit_now_medium['reasoning'],
            pros=pit_now_medium['pros'],
            cons=pit_now_medium['cons'],
            ai_confidence=pit_now_medium['confidence']
        ))

        # Option 2: STAY OUT 3 more laps
        stay_out = self._calculate_stay_out_impact(lap_number, 3, laps_remaining)
        options.append(DecisionOption(
            option_id=2,
            category='PIT_STOP',
            title='Stay Out - Extend Stint',
            description=f'Stay out for 3 more laps (pit lap {lap_number + 3})',
            action='STAY_OUT',
            parameters={'extend_laps': 3},
            predicted_lap_time_impact=stay_out['lap_time_impact'],
            predicted_race_time_impact=stay_out['race_time_impact'],
            tire_wear_impact=stay_out['tire_wear'],
            reasoning=stay_out['reasoning'],
            pros=stay_out['pros'],
            cons=stay_out['cons'],
            ai_confidence=stay_out['confidence']
        ))

        # Option 3: PIT NOW for HARD tires (alternative strategy)
        pit_now_hard = self._calculate_pit_impact(lap_number, 'HARD', laps_remaining)
        options.append(DecisionOption(
            option_id=3,
            category='PIT_STOP',
            title='Pit Now - Hard Tires',
            description=f'Box this lap for HARD compound (long stint to end)',
            action='PIT_NOW',
            parameters={'compound': 'HARD'},
            predicted_lap_time_impact=-25.0,
            predicted_race_time_impact=pit_now_hard['race_time_impact'],
            tire_wear_impact=0.0,
            reasoning=pit_now_hard['reasoning'],
            pros=pit_now_hard['pros'],
            cons=pit_now_hard['cons'],
            ai_confidence=pit_now_hard['confidence']
        ))

        # Sort by AI confidence (HIGHLY_RECOMMENDED first)
        confidence_order = {'HIGHLY_RECOMMENDED': 0, 'RECOMMENDED': 1, 'ALTERNATIVE': 2, 'NOT_RECOMMENDED': 3}
        options.sort(key=lambda x: confidence_order.get(x.ai_confidence, 99))

        # Re-number option_ids after sorting
        for i, opt in enumerate(options, 1):
            opt.option_id = i

        return options

    def _generate_driving_style_options(self, lap_number: int, context: Dict) -> List[DecisionOption]:
        """Generate driving style options"""
        options = []

        # Option 1: AGGRESSIVE
        options.append(DecisionOption(
            option_id=1,
            category='DRIVING_STYLE',
            title='Aggressive Driving',
            description='Push hard - prioritize track position over tire life',
            action='SET_STYLE',
            parameters={'style': DrivingStyle.AGGRESSIVE},
            predicted_lap_time_impact=-0.3,
            predicted_race_time_impact=-10.0,  # Faster but more pit stops
            tire_wear_impact=1.4,
            reasoning='Start strong, gain positions early while tires are fresh',
            pros=['Faster lap times (-0.3s/lap)', 'Better overtaking', 'Build gap to cars behind'],
            cons=['Higher tire wear (40% more)', 'May require earlier pit stop', 'Fuel consumption +15%'],
            ai_confidence='RECOMMENDED'
        ))

        # Option 2: BALANCED
        options.append(DecisionOption(
            option_id=2,
            category='DRIVING_STYLE',
            title='Balanced Driving',
            description='Standard race pace - manage tires and position',
            action='SET_STYLE',
            parameters={'style': DrivingStyle.BALANCED},
            predicted_lap_time_impact=0.0,
            predicted_race_time_impact=0.0,
            tire_wear_impact=1.0,
            reasoning='Consistent performance, predictable strategy, room to adjust later',
            pros=['Predictable tire wear', 'Standard fuel usage', 'Flexibility for later'],
            cons=['No immediate advantage', 'May lose positions to aggressive drivers'],
            ai_confidence='HIGHLY_RECOMMENDED'
        ))

        # Option 3: CONSERVATIVE
        options.append(DecisionOption(
            option_id=3,
            category='DRIVING_STYLE',
            title='Conservative Driving',
            description='Save tires - extend stint, fewer pit stops',
            action='SET_STYLE',
            parameters={'style': DrivingStyle.CONSERVATIVE},
            predicted_lap_time_impact=0.4,
            predicted_race_time_impact=5.0,  # Slower now, but saves pit stop later
            tire_wear_impact=0.7,
            reasoning='Long first stint, potentially go to end without second stop',
            pros=['Low tire wear (-30%)', 'Extended stint length', 'Fuel saving'],
            cons=['Slower lap times (+0.4s/lap)', 'May lose track position early'],
            ai_confidence='ALTERNATIVE'
        ))

        return options

    def _generate_tactical_options(self, lap_number: int, context: Dict) -> List[DecisionOption]:
        """Generate mid-race tactical options"""
        # Similar structure - push vs conserve vs maintain
        gap_ahead = context.get('gap_ahead', 3.0)

        options = [
            DecisionOption(
                option_id=1,
                category='TACTIC',
                title='Push Hard - Close Gap',
                description=f'Attack mode - close {gap_ahead:.1f}s gap ahead',
                action='SET_STYLE',
                parameters={'style': DrivingStyle.AGGRESSIVE},
                predicted_lap_time_impact=-0.3,
                predicted_race_time_impact=2.0,
                tire_wear_impact=1.4,
                reasoning=f'Gap to leader is {gap_ahead:.1f}s - attackable with fresh tires',
                pros=['Close gap', 'Pressure leader', 'Overtaking opportunity'],
                cons=['High tire wear', 'May need earlier next pit'],
                ai_confidence='RECOMMENDED'
            ),
            DecisionOption(
                option_id=2,
                category='TACTIC',
                title='Maintain Pace',
                description='Hold current position, manage tires',
                action='SET_STYLE',
                parameters={'style': DrivingStyle.BALANCED},
                predicted_lap_time_impact=0.0,
                predicted_race_time_impact=0.0,
                tire_wear_impact=1.0,
                reasoning='Comfortable position, no immediate threats',
                pros=['Tire preservation', 'Predictable strategy'],
                cons=['Gap may increase'],
                ai_confidence='HIGHLY_RECOMMENDED'
            ),
            DecisionOption(
                option_id=3,
                category='TACTIC',
                title='Conserve Tires',
                description='Back off, save tires for later attack',
                action='SET_STYLE',
                parameters={'style': DrivingStyle.CONSERVATIVE},
                predicted_lap_time_impact=0.4,
                predicted_race_time_impact=-3.0,
                tire_wear_impact=0.7,
                reasoning='Build tire advantage for final stint attack',
                pros=['Fresh tires later', 'Undercut opportunity'],
                cons=['Lose track position now'],
                ai_confidence='ALTERNATIVE'
            )
        ]

        return options

    def _generate_final_laps_options(self, lap_number: int, context: Dict) -> List[DecisionOption]:
        """Generate final laps attack vs manage options"""
        laps_remaining = self.total_laps - lap_number

        options = [
            DecisionOption(
                option_id=1,
                category='TACTIC',
                title='Quali Mode - All Out Attack',
                description=f'Maximum attack for final {laps_remaining} laps',
                action='SET_STYLE',
                parameters={'style': DrivingStyle.QUALI_MODE},
                predicted_lap_time_impact=-0.8,
                predicted_race_time_impact=-2.0,
                tire_wear_impact=3.0,
                reasoning='Final laps - tire life no longer matters, go for it',
                pros=['Maximum pace', 'Overtaking boost', 'No tire saving needed'],
                cons=['Extreme tire wear (irrelevant)', 'High fuel usage'],
                ai_confidence='HIGHLY_RECOMMENDED'
            ),
            DecisionOption(
                option_id=2,
                category='TACTIC',
                title='Push Hard - Controlled Attack',
                description='Aggressive but sustainable pace',
                action='SET_STYLE',
                parameters={'style': DrivingStyle.AGGRESSIVE},
                predicted_lap_time_impact=-0.3,
                predicted_race_time_impact=-0.5,
                tire_wear_impact=1.4,
                reasoning='Strong push with margin for error',
                pros=['Fast pace', 'Lower risk'],
                cons=['Not maximum attack'],
                ai_confidence='RECOMMENDED'
            ),
            DecisionOption(
                option_id=3,
                category='TACTIC',
                title='Secure Position',
                description='Manage to finish, no risks',
                action='SET_STYLE',
                parameters={'style': DrivingStyle.BALANCED},
                predicted_lap_time_impact=0.0,
                predicted_race_time_impact=0.0,
                tire_wear_impact=1.0,
                reasoning='Position secure, bring it home',
                pros=['Safe finish', 'No mistakes'],
                cons=['May lose positions'],
                ai_confidence='ALTERNATIVE'
            )
        ]

        return options

    def _calculate_pit_impact(self, lap_number: int, compound: str, laps_remaining: int) -> Dict:
        """Calculate predicted impact of pitting now for given compound"""
        # Use tire model to calculate optimal pit window
        scenarios = self.tire_model.optimal_pit_window(
            current_lap=lap_number,
            stint1_compound=self.state.tire_compound,
            stint2_compound=compound
        )

        # Find scenario for pitting this lap
        pit_now_scenario = next((s for s in scenarios if s['pit_lap'] == lap_number), scenarios[0])
        optimal_scenario = scenarios[0]

        time_delta = pit_now_scenario['total_race_time'] - optimal_scenario['total_race_time']

        confidence = 'HIGHLY_RECOMMENDED' if time_delta < 1.0 else 'RECOMMENDED' if time_delta < 3.0 else 'ALTERNATIVE'

        return {
            'race_time_impact': time_delta,
            'reasoning': f'Pit now for {compound} - {laps_remaining} laps remaining on fresh tires',
            'pros': [f'Fresh {compound} tires', f'{laps_remaining} laps to end', 'Clear track ahead'],
            'cons': ['25s pit loss', 'Lose track position', 'Undercut risk from behind'],
            'confidence': confidence
        }

    def _calculate_stay_out_impact(self, lap_number: int, extend_laps: int, laps_remaining: int) -> Dict:
        """
        Calculate impact of staying out N more laps
        Uses tire model to calculate FULL RACE impact, not just next 3 laps
        """
        current_tire_age = self.state.tire_age

        # Calculate total race time if we stay out to lap_number + extend_laps, then pit
        future_pit_lap = lap_number + extend_laps

        # Simulate staying out: calculate time from current lap to future pit lap
        stay_out_time = 0
        tire_age = current_tire_age
        for lap in range(lap_number, future_pit_lap):
            laptime = self.tire_model.calculate_laptime(lap, tire_age, self.state.tire_compound)
            stay_out_time += laptime
            tire_age += 1

        # After staying out, we'd pit and run remaining laps on fresh tires
        # Use MEDIUM as default second stint compound
        remaining_laps_after_pit = self.total_laps - future_pit_lap
        if remaining_laps_after_pit > 0:
            second_stint_time = self.tire_model.calculate_stint_time(
                start_lap=future_pit_lap + 1,
                end_lap=self.total_laps,
                compound='MEDIUM',
                tire_age_start=1
            )
            total_stay_out_strategy = stay_out_time + 25.0 + second_stint_time  # Include pit stop
        else:
            # Staying out to the end (no second pit)
            total_stay_out_strategy = stay_out_time

        # Calculate total race time if we pit NOW
        pit_now_time = 25.0  # Pit stop loss
        remaining_laps_after_pit_now = self.total_laps - lap_number
        if remaining_laps_after_pit_now > 0:
            stint_on_fresh = self.tire_model.calculate_stint_time(
                start_lap=lap_number + 1,
                end_lap=self.total_laps,
                compound='MEDIUM',
                tire_age_start=1
            )
            total_pit_now_strategy = pit_now_time + stint_on_fresh
        else:
            total_pit_now_strategy = 0

        # Race time impact = (stay out strategy) - (pit now strategy)
        # Negative = stay out is faster, Positive = pit now is faster
        race_time_impact = total_stay_out_strategy - total_pit_now_strategy

        # Lap time impact for next stint
        wear_rate = self.tire_model.get_tire_wear_rate(self.state.tire_compound, current_tire_age + extend_laps)
        lap_time_impact = wear_rate

        # AI confidence based on ACTUAL full race impact
        if race_time_impact < -15.0:
            confidence = 'HIGHLY_RECOMMENDED'  # Saves >15s total
        elif race_time_impact < 0:
            confidence = 'RECOMMENDED'  # Saves time
        elif race_time_impact < 30.0:
            confidence = 'ALTERNATIVE'  # Close call
        else:
            confidence = 'NOT_RECOMMENDED'  # Pit now is much faster!

        return {
            'lap_time_impact': lap_time_impact,
            'race_time_impact': race_time_impact,
            'tire_wear': 1.0 + (0.1 * extend_laps),
            'reasoning': f'Extend stint {extend_laps} laps - delay pit stop, build undercut window',
            'pros': ['No pit loss yet', 'Undercut cars ahead', 'Track position maintained'],
            'cons': [f'Tire age will be {current_tire_age + extend_laps} laps', 'Performance degradation', 'Risk of tire cliff'],
            'confidence': confidence
        }

    def execute_decision(self, option: DecisionOption) -> Dict:
        """
        Execute user's chosen decision option

        Args:
            option: The DecisionOption the user selected

        Returns:
            Execution result with updated state
        """
        result = {
            'success': True,
            'action_taken': option.action,
            'lap': self.state.current_lap,
            'message': ''
        }

        if option.action == 'PIT_NOW':
            # Execute pit stop
            compound = option.parameters['compound']
            self.state.pit_stops.append({
                'lap': self.state.current_lap,
                'compound': compound,
                'reason': option.title
            })

            # Update tire state
            self.state.tire_compound = compound
            self.state.tire_age = 1  # Fresh tires

            # Add pit time loss
            self.state.total_race_time += 25.0

            result['message'] = f'✅ Pitted for {compound} tires (25s loss)'

        elif option.action == 'STAY_OUT':
            # Just continue - no state change
            extend_laps = option.parameters.get('extend_laps', 0)
            result['message'] = f'✅ Staying out - extending stint {extend_laps} laps'

        elif option.action == 'SET_STYLE':
            # Change driving style
            new_style = option.parameters['style']
            old_style = self.state.driving_style

            self.state.driving_style = new_style
            self.style_manager.set_style(new_style, self.state.current_lap, option.title)

            # Update tire model with new wear multiplier
            self.tire_model.driving_style_multiplier = self.style_manager.get_tire_wear_multiplier()

            result['message'] = f'✅ Driving style: {old_style.value} → {new_style.value}'

        # Record decision
        self.state.decisions_made.append({
            'lap': self.state.current_lap,
            'option_id': option.option_id,
            'category': option.category,
            'title': option.title,
            'action': option.action
        })

        return result

    def get_final_comparison(self) -> Dict:
        """
        Compare user's race to actual Bahrain 2024 results
        Calculate where user would finish on the leaderboard

        Returns:
            Comparison results with leaderboard position
        """
        user_time = self.state.total_race_time
        comparison_time = self.comparison_total_time
        delta = user_time - comparison_time

        # Calculate leaderboard position by comparing to all drivers
        leaderboard = []
        for driver_code in self.session.drivers:
            try:
                laps = self.session.laps.pick_driver(driver_code)
                if len(laps) > 0:
                    laptimes = laps['LapTime'].dt.total_seconds()
                    total_time = laptimes.sum()
                    driver_info = self.session.get_driver(driver_code)

                    leaderboard.append({
                        'driver': driver_code,
                        'team': driver_info.get('TeamName', 'Unknown'),
                        'time': total_time
                    })
            except:
                pass

        # Add user's time to leaderboard
        leaderboard.append({
            'driver': 'YOU',
            'team': 'Your Strategy',
            'time': user_time
        })

        # Sort by time
        leaderboard.sort(key=lambda x: x['time'])

        # Find user's position
        user_position = next(i+1 for i, d in enumerate(leaderboard) if d['driver'] == 'YOU')
        gap_to_winner = user_time - leaderboard[0]['time']

        # Get nearby drivers (±2 positions)
        nearby_start = max(0, user_position - 3)
        nearby_end = min(len(leaderboard), user_position + 2)
        nearby_drivers = leaderboard[nearby_start:nearby_end]

        # Calculate if user would have won
        result = 'WON' if delta < 0 else 'LOST'

        return {
            'result': result,
            'user_time': user_time,
            'comparison_driver': self.comparison_driver,
            'comparison_time': comparison_time,
            'time_delta': delta,
            'pit_stops': len(self.state.pit_stops),
            'pit_stop_details': self.state.pit_stops,
            'decisions_made': len(self.state.decisions_made),
            'decision_timeline': self.state.decisions_made,
            'leaderboard_position': user_position,
            'total_drivers': len(leaderboard),
            'gap_to_winner': gap_to_winner,
            'nearby_drivers': nearby_drivers,
            'full_leaderboard': leaderboard[:10]  # Top 10
        }


if __name__ == '__main__':
    """Test interactive race simulator"""

    print("="*70)
    print("🎮 INTERACTIVE RACE SIMULATOR TEST")
    print("="*70)

    # Create simulator for Bahrain 2024
    sim = InteractiveRaceSimulator(
        race_year=2024,
        race_name='Bahrain',
        total_laps=57,
        comparison_driver='VER'
    )

    # Start race
    race_info = sim.start_race(starting_position=3, starting_compound='SOFT')

    # Test decision generation at lap 12 (first pit window)
    print("\n" + "="*70)
    print("📊 LAP 12 - FIRST PIT WINDOW DECISION")
    print("="*70)

    sim.state.current_lap = 12
    sim.state.tire_age = 12

    options = sim.generate_decision_options(lap_number=12)

    for i, option in enumerate(options, 1):
        print(f"\n🎯 OPTION {i}: {option.title}")
        print(f"   {option.description}")
        print(f"   Reasoning: {option.reasoning}")
        print(f"   Race time impact: {option.predicted_race_time_impact:+.1f}s")
        print(f"   AI confidence: {option.ai_confidence}")
        print(f"   Pros: {', '.join(option.pros)}")
        print(f"   Cons: {', '.join(option.cons)}")

    # Simulate user choosing option 1 (pit now)
    print(f"\n{'='*70}")
    print("👤 USER DECISION: Option 1 (Pit Now - Medium Tires)")
    print("="*70)

    result = sim.execute_decision(options[0])
    print(f"   {result['message']}")
    print(f"   Tire state: {sim.state.tire_compound}, {sim.state.tire_age} laps old")
    print(f"   Total race time: {sim.state.total_race_time:.1f}s")

    # Simulate some laps
    print(f"\n{'='*70}")
    print("🏎️  SIMULATING LAPS 13-20...")
    print("="*70)

    for lap in range(13, 21):
        sim.state.current_lap = lap
        lap_time, lap_info = sim.simulate_lap(lap)
        print(f"   Lap {lap}: {lap_time:.2f}s (tire age: {lap_info['tire_age']}, total: {lap_info['cumulative_time']:.1f}s)")

    print(f"\n{'='*70}")
    print("✅ Interactive Race Simulator working!")
    print("="*70)
