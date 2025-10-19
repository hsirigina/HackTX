"""
Driving Style Management System
Controls how driving style affects tire wear, lap times, and race strategy
"""

from typing import Dict, Optional
from enum import Enum

class DrivingStyle(Enum):
    """Available driving styles with different trade-offs"""
    AGGRESSIVE = "AGGRESSIVE"      # Fast laps, high tire wear
    BALANCED = "BALANCED"          # Moderate pace, moderate wear
    CONSERVATIVE = "CONSERVATIVE"  # Slow laps, low tire wear
    QUALI_MODE = "QUALI_MODE"      # Maximum attack, extreme wear (1-2 laps only)
    TIRE_SAVE = "TIRE_SAVE"        # Extreme conservation, very slow


class DrivingStyleManager:
    """
    Manages driving style settings and their impact on race performance

    Engineer can adjust style, system recalculates strategy accordingly
    """

    # Style characteristics
    STYLE_PROFILES = {
        DrivingStyle.AGGRESSIVE: {
            'lap_time_delta': -0.3,      # 0.3s faster per lap
            'tire_wear_multiplier': 1.4,  # 40% more tire wear
            'fuel_multiplier': 1.15,      # 15% more fuel consumption
            'overtaking_bonus': 0.25,     # 25% better overtaking probability
            'risk_level': 'HIGH',
            'description': 'Maximum attack - push tire limits for track position',
            'recommended_when': 'Undercut opportunity, defending position, clear track ahead'
        },

        DrivingStyle.BALANCED: {
            'lap_time_delta': 0.0,        # Normal pace
            'tire_wear_multiplier': 1.0,  # Standard wear
            'fuel_multiplier': 1.0,       # Standard fuel
            'overtaking_bonus': 0.0,      # Normal overtaking
            'risk_level': 'MEDIUM',
            'description': 'Race pace - consistent performance, predictable wear',
            'recommended_when': 'Normal racing conditions, managing gaps'
        },

        DrivingStyle.CONSERVATIVE: {
            'lap_time_delta': 0.4,        # 0.4s slower per lap
            'tire_wear_multiplier': 0.7,  # 30% less tire wear
            'fuel_multiplier': 0.90,      # 10% less fuel
            'overtaking_bonus': -0.15,    # 15% worse overtaking
            'risk_level': 'LOW',
            'description': 'Tire preservation - extend stint, avoid pit stops',
            'recommended_when': 'Track position secure, long stint planned, high deg track'
        },

        DrivingStyle.QUALI_MODE: {
            'lap_time_delta': -0.8,       # 0.8s faster (extreme)
            'tire_wear_multiplier': 3.0,  # 3x tire wear (unsustainable)
            'fuel_multiplier': 1.30,      # 30% more fuel
            'overtaking_bonus': 0.50,     # 50% overtaking boost
            'risk_level': 'CRITICAL',
            'description': 'Qualifying pace - maximum attack for 1-2 laps only',
            'recommended_when': 'Desperate overtake attempt, DRS battle, last lap push'
        },

        DrivingStyle.TIRE_SAVE: {
            'lap_time_delta': 0.8,        # 0.8s slower (extreme)
            'tire_wear_multiplier': 0.5,  # 50% wear (heavy conservation)
            'fuel_multiplier': 0.85,      # 15% less fuel
            'overtaking_bonus': -0.30,    # 30% worse overtaking
            'risk_level': 'MINIMAL',
            'description': 'Maximum tire saving - no-stop strategy attempt',
            'recommended_when': 'No-stop strategy, safety car imminent, huge gap behind'
        }
    }

    def __init__(self, initial_style: DrivingStyle = DrivingStyle.BALANCED):
        """Initialize with a driving style"""
        self.current_style = initial_style
        self.style_history = []  # Track style changes throughout race
        self.laps_in_current_style = 0

    def set_style(self, new_style: DrivingStyle, lap_number: int, reason: str = "Engineer override"):
        """
        Change driving style (engineer decision)

        Args:
            new_style: New DrivingStyle to adopt
            lap_number: Current lap number
            reason: Why style is changing
        """
        if new_style != self.current_style:
            # Record the change
            self.style_history.append({
                'lap': lap_number,
                'from_style': self.current_style,
                'to_style': new_style,
                'reason': reason,
                'laps_in_previous': self.laps_in_current_style
            })

            self.current_style = new_style
            self.laps_in_current_style = 0

            print(f"\n🎮 DRIVING STYLE CHANGE (Lap {lap_number}):")
            print(f"   {new_style.value}")
            print(f"   Reason: {reason}")
            print(f"   Impact: {self._format_impact(new_style)}")

        self.laps_in_current_style += 1

    def _format_impact(self, style: DrivingStyle) -> str:
        """Format style impact for display"""
        profile = self.STYLE_PROFILES[style]
        lap_delta = profile['lap_time_delta']
        wear_mult = profile['tire_wear_multiplier']

        lap_str = f"{abs(lap_delta):.1f}s {'faster' if lap_delta < 0 else 'slower'}"
        wear_str = f"{abs(wear_mult - 1.0)*100:.0f}% {'more' if wear_mult > 1 else 'less'} tire wear"

        return f"{lap_str}, {wear_str}"

    def get_lap_time_adjustment(self) -> float:
        """Get lap time delta for current style"""
        return self.STYLE_PROFILES[self.current_style]['lap_time_delta']

    def get_tire_wear_multiplier(self) -> float:
        """Get tire wear multiplier for current style"""
        return self.STYLE_PROFILES[self.current_style]['tire_wear_multiplier']

    def get_fuel_multiplier(self) -> float:
        """Get fuel consumption multiplier"""
        return self.STYLE_PROFILES[self.current_style]['fuel_multiplier']

    def get_overtaking_bonus(self) -> float:
        """Get overtaking probability bonus/penalty"""
        return self.STYLE_PROFILES[self.current_style]['overtaking_bonus']

    def recommend_style(
        self,
        current_situation: Dict,
        tire_age: int,
        laps_remaining: int,
        gap_ahead: Optional[float],
        gap_behind: Optional[float]
    ) -> Dict:
        """
        AI recommendation for which driving style to use

        Args:
            current_situation: Current race state
            tire_age: Current tire age in laps
            laps_remaining: Laps until race end
            gap_ahead: Gap to car ahead (seconds)
            gap_behind: Gap to car behind (seconds)

        Returns:
            {
                'recommended_style': DrivingStyle,
                'reason': str,
                'urgency': str,
                'alternative_styles': List[DrivingStyle]
            }
        """
        recommendations = []

        # Scenario 1: Tire degradation critical
        if tire_age > 30:
            recommendations.append({
                'style': DrivingStyle.CONSERVATIVE,
                'reason': f'Tire age {tire_age} laps - preserve rubber',
                'priority': 8,
                'urgency': 'HIGH'
            })

        # Scenario 2: Undercut opportunity
        if gap_ahead and gap_ahead < 3.0 and tire_age < 15:
            recommendations.append({
                'style': DrivingStyle.AGGRESSIVE,
                'reason': f'Gap ahead {gap_ahead:.1f}s - undercut opportunity',
                'priority': 9,
                'urgency': 'CRITICAL'
            })

        # Scenario 3: Under pressure from behind
        if gap_behind and gap_behind < 2.0:
            recommendations.append({
                'style': DrivingStyle.AGGRESSIVE,
                'reason': f'Gap behind {gap_behind:.1f}s - defend position',
                'priority': 7,
                'urgency': 'HIGH'
            })

        # Scenario 4: Clear air - save tires
        if (not gap_ahead or gap_ahead > 5.0) and (not gap_behind or gap_behind > 5.0):
            recommendations.append({
                'style': DrivingStyle.BALANCED,
                'reason': 'Clear air - manage pace, no threats',
                'priority': 5,
                'urgency': 'LOW'
            })

        # Scenario 5: Final laps push
        if laps_remaining <= 3 and gap_ahead and gap_ahead < 1.5:
            recommendations.append({
                'style': DrivingStyle.QUALI_MODE,
                'reason': 'Final laps - all-out attack for position',
                'priority': 10,
                'urgency': 'CRITICAL'
            })

        # Scenario 6: Long stint strategy
        if laps_remaining > 20 and tire_age < 10:
            recommendations.append({
                'style': DrivingStyle.TIRE_SAVE,
                'reason': 'Long stint ahead - extreme tire saving',
                'priority': 6,
                'urgency': 'MEDIUM'
            })

        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)

        if recommendations:
            top_rec = recommendations[0]
            return {
                'recommended_style': top_rec['style'],
                'reason': top_rec['reason'],
                'urgency': top_rec['urgency'],
                'alternative_styles': [r['style'] for r in recommendations[1:3]],
                'all_recommendations': recommendations
            }
        else:
            # Default to balanced
            return {
                'recommended_style': DrivingStyle.BALANCED,
                'reason': 'Standard racing conditions',
                'urgency': 'LOW',
                'alternative_styles': []
            }

    def get_current_profile(self) -> Dict:
        """Get full profile of current style"""
        profile = self.STYLE_PROFILES[self.current_style].copy()
        profile['style_name'] = self.current_style.value
        profile['laps_in_style'] = self.laps_in_current_style
        return profile

    def get_style_comparison(self) -> str:
        """
        Get formatted comparison of all styles for engineer display
        """
        output = "\n🎮 AVAILABLE DRIVING STYLES:\n"
        output += "="*70 + "\n"

        for style in DrivingStyle:
            profile = self.STYLE_PROFILES[style]
            current = "👉 " if style == self.current_style else "   "

            output += f"\n{current}{style.value}:\n"
            output += f"   {profile['description']}\n"
            output += f"   Lap time: {profile['lap_time_delta']:+.1f}s | "
            output += f"Tire wear: {profile['tire_wear_multiplier']:.1f}x | "
            output += f"Risk: {profile['risk_level']}\n"
            output += f"   Use when: {profile['recommended_when']}\n"

        return output


if __name__ == '__main__':
    """Test driving style system"""

    print("="*70)
    print("🎮 DRIVING STYLE SYSTEM TEST")
    print("="*70)

    manager = DrivingStyleManager()

    # Show all styles
    print(manager.get_style_comparison())

    # Simulate race scenarios
    print("\n" + "="*70)
    print("📊 SCENARIO TESTING:")
    print("="*70)

    # Scenario 1: Undercut opportunity
    print("\n1️⃣ Undercut Opportunity (Lap 20, fresh tires, 2.5s gap ahead)")
    rec = manager.recommend_style(
        current_situation={},
        tire_age=5,
        laps_remaining=37,
        gap_ahead=2.5,
        gap_behind=5.0
    )
    print(f"   Recommended: {rec['recommended_style'].value}")
    print(f"   Reason: {rec['reason']}")
    print(f"   Urgency: {rec['urgency']}")

    # Scenario 2: Tire saving
    print("\n2️⃣ Tire Preservation (Lap 40, old tires, clear air)")
    rec = manager.recommend_style(
        current_situation={},
        tire_age=35,
        laps_remaining=17,
        gap_ahead=8.0,
        gap_behind=10.0
    )
    print(f"   Recommended: {rec['recommended_style'].value}")
    print(f"   Reason: {rec['reason']}")

    # Scenario 3: Final lap battle
    print("\n3️⃣ Final Lap Battle (Lap 55, 1.2s behind leader)")
    rec = manager.recommend_style(
        current_situation={},
        tire_age=15,
        laps_remaining=2,
        gap_ahead=1.2,
        gap_behind=None
    )
    print(f"   Recommended: {rec['recommended_style'].value}")
    print(f"   Reason: {rec['reason']}")
    print(f"   Urgency: {rec['urgency']}")

    print("\n" + "="*70)
    print("✅ Driving style system ready for integration!")
    print("="*70 + "\n")
