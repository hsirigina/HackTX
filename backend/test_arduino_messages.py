"""
Test Arduino Display Messages
Send test messages to the driver display via Supabase
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*60)
print("ARDUINO DISPLAY TEST MESSAGES")
print("="*60)
print("\nSelect a test message to send:")
print("\n1. 🏁 PIT NOW (urgent pit stop with buzzer)")
print("2. 🔔 ENGINEER ALERT (engineer needs attention)")
print("3. ⏱️  PIT COUNTDOWN (3 laps to pit)")
print("4. 📊 STRATEGY UPDATE (custom message)")
print("5. 📍 LAP UPDATE (lap 45/78, P1, +2.3s)")
print("6. 💬 CUSTOM MESSAGE (type your own)")
print("7. 🧹 CLEAR (back to F1 DRIVER READY)")
print("\n0. Exit")
print("="*60)

while True:
    choice = input("\nEnter choice (0-7): ").strip()
    
    if choice == '0':
        print("\n👋 Goodbye!")
        break
    
    elif choice == '1':
        # PIT NOW - highest priority
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'PIT_NOW',
            'content': {'message': 'BOX BOX BOX'},
            'priority': 10,
            'acknowledged': False
        }).execute()
        print("✅ Sent: PIT NOW (with buzzer!)")
    
    elif choice == '2':
        # ENGINEER ALERT
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'ENGINEER_ALERT',
            'content': {'message': 'Check radio'},
            'priority': 5,
            'acknowledged': False
        }).execute()
        print("✅ Sent: ENGINEER ALERT")
    
    elif choice == '3':
        # PIT COUNTDOWN
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'PIT_COUNTDOWN',
            'content': {'laps': 3},
            'priority': 3,
            'acknowledged': False
        }).execute()
        print("✅ Sent: PIT COUNTDOWN (3 laps)")
    
    elif choice == '4':
        # STRATEGY UPDATE
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'STRATEGY',
            'content': {'message': 'PUSH HARD!'},
            'priority': 2,
            'acknowledged': False
        }).execute()
        print("✅ Sent: STRATEGY UPDATE")
    
    elif choice == '5':
        # LAP UPDATE
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'LAP_UPDATE',
            'content': {
                'current_lap': 45,
                'total_laps': 78,
                'position': 'P1',
                'gap': '+2.3s'
            },
            'priority': 1,
            'acknowledged': False
        }).execute()
        print("✅ Sent: LAP UPDATE")
    
    elif choice == '6':
        # CUSTOM MESSAGE
        msg = input("Enter your message (max ~18 chars for display): ")
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'STRATEGY',
            'content': {'message': msg},
            'priority': 1,
            'acknowledged': False
        }).execute()
        print(f"✅ Sent: {msg}")
    
    elif choice == '7':
        # CLEAR - back to default
        supabase.table('driver_display').insert({
            'race_id': 'test_race',
            'message_type': 'CLEAR',
            'content': {'message': 'Clear display'},
            'priority': 0,
            'acknowledged': False
        }).execute()
        print("✅ Sent: CLEAR (back to F1 DRIVER READY)")
    
    else:
        print("❌ Invalid choice. Please enter 0-7")
    
    time.sleep(0.5)

