"""
Arduino Controller - Simplified interface for sending commands to driver display
Use this from your gesture system or race monitor
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from typing import Optional
import time

load_dotenv()


class ArduinoController:
    """Controller for sending messages to driver display via Supabase"""
    
    def __init__(self, race_id: str = None):
        """
        Initialize Arduino controller
        
        Args:
            race_id: Unique race identifier (e.g., 'monaco_2024')
        """
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.supabase = create_client(supabase_url, supabase_key)
        self.race_id = race_id or f"race_{int(time.time())}"
    
    def send_message(self, message_type: str, content: dict, priority: int = 0):
        """
        Send a message to driver display
        
        Args:
            message_type: Type of message ('PIT_NOW', 'ENGINEER_ALERT', 'STRATEGY', etc.)
            content: Message content as dict
            priority: Priority level (0-10, higher = more urgent)
        """
        try:
            result = self.supabase.table('driver_display').insert({
                'race_id': self.race_id,
                'message_type': message_type,
                'content': content,
                'priority': priority,
                'acknowledged': False
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def send_pit_now(self, lap: Optional[int] = None, compound: str = "MEDIUM"):
        """Send urgent pit stop command (will trigger buzzer)"""
        return self.send_message(
            'PIT_NOW',
            {
                'message': 'PIT NOW - BOX BOX BOX',
                'lap': lap,
                'compound': compound
            },
            priority=10
        )
    
    def send_pit_countdown(self, laps: int):
        """Send pit countdown"""
        return self.send_message(
            'PIT_COUNTDOWN',
            {
                'laps': laps,
                'message': f'Pit in {laps} laps'
            },
            priority=7
        )
    
    def send_strategy_update(self, strategy_name: str, details: str):
        """Send strategy update (no buzzer)"""
        return self.send_message(
            'STRATEGY',
            {
                'strategy': strategy_name,
                'message': details
            },
            priority=3
        )
    
    def send_lap_update(self, current_lap: int, total_laps: int, position: str, gap: str):
        """Send lap update"""
        return self.send_message(
            'LAP_UPDATE',
            {
                'current_lap': current_lap,
                'total_laps': total_laps,
                'position': position,
                'gap': gap
            },
            priority=1
        )
    
    def clear_display(self):
        """Clear display to monitoring state"""
        return self.send_message(
            'CLEAR',
            {'message': 'Return to monitoring'},
            priority=0
        )
    
    def get_recent_messages(self, limit: int = 10):
        """Get recent messages"""
        try:
            result = self.supabase.table('driver_display')\
                .select('*')\
                .eq('race_id', self.race_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []


# Example usage
if __name__ == "__main__":
    controller = ArduinoController(race_id='monaco_2024_test')
    
    print("Arduino Controller Test")
    print("=" * 60)
    
    # Test sequence
    print("\n1. Sending lap update...")
    controller.send_lap_update(65, 78, 'P1', '+2.3')
    time.sleep(2)
    
    print("\n2. Sending pit countdown...")
    controller.send_pit_countdown(3)
    time.sleep(2)
    
    print("\n3. Sending PIT NOW (will buzz)...")
    controller.send_pit_now(lap=68, compound='SOFT')
    time.sleep(3)
    
    print("\n4. Clearing display...")
    controller.clear_display()
    
    print("\n5. Recent messages:")
    messages = controller.get_recent_messages(5)
    for msg in messages:
        print(f"   - {msg['message_type']}: {msg['content']}")
    
    print("\n✅ Test complete!")
