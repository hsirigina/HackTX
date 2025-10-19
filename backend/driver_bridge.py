"""
Driver Display Bridge
Polls Supabase and sends updates to Driver Arduino (Nano)
"""

import serial
import os
import sys
import time
from supabase import create_client
from dotenv import load_dotenv
import serial.tools.list_ports

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Find Arduino port
def find_arduino_port():
    """Find Arduino serial port automatically"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'usbserial' in port.device.lower() or 'usbmodem' in port.device.lower() or 'arduino' in port.description.lower():
            return port.device
    return None

SERIAL_PORT = find_arduino_port()

if not SERIAL_PORT:
    print("\n🔍 Available serial ports:")
    ports = serial.tools.list_ports.comports()
    for i, port in enumerate(ports):
        print(f"  [{i}] {port.device} - {port.description}")
    
    if ports:
        choice = input("\nEnter port number (or full path like /dev/tty.usbserial-XXX): ")
        if choice.isdigit() and 0 <= int(choice) < len(ports):
            SERIAL_PORT = ports[int(choice)].device
        else:
            SERIAL_PORT = choice
    else:
        print("❌ No serial ports found. Make sure Arduino is connected.")
        sys.exit(1)

print(f"\n📡 Connecting to Driver Arduino on {SERIAL_PORT}...")

try:
    arduino = serial.Serial(SERIAL_PORT, 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino reset
    print("✅ Driver Display connected!")
except serial.SerialException as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("DRIVER DISPLAY BRIDGE RUNNING")
print("="*60)
print("Polling Supabase for messages...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

last_check = time.time()
last_message_id = 0
message_count = 0
POLL_INTERVAL = 1.0  # Check Supabase every second

try:
    while True:
        # Read any responses from Arduino
        if arduino.in_waiting:
            line = arduino.readline().decode().strip()
            if line:
                print(f"📟 Arduino: {line}")
        
        # Poll Supabase
        if time.time() - last_check > POLL_INTERVAL:
            last_check = time.time()
            
            try:
                # Get latest unacknowledged message
                result = supabase.table('driver_display')\
                    .select('*')\
                    .eq('acknowledged', False)\
                    .order('priority', desc=True)\
                    .order('id', desc=True)\
                    .limit(1)\
                    .execute()
                
                if result.data and len(result.data) > 0:
                    msg = result.data[0]
                    
                    # Only process if it's a new message
                    if msg['id'] > last_message_id:
                        last_message_id = msg['id']
                        message_count += 1
                        msg_type = msg['message_type']
                        content = msg['content']
                        
                        print(f"\n📨 Message #{message_count}: {msg_type} (ID: {msg['id']}, Priority: {msg['priority']})")
                        
                        if msg_type == 'ENGINEER_ALERT':
                            # Engineer touched sensor
                            arduino.write(b'ENGINEER_ALERT\n')
                            print("   🔔 Sent engineer alert to driver display")
                        
                        elif msg_type == 'PIT_NOW':
                            # Pit stop - show message AND buzz
                            arduino.write(b'PIT_NOW\n')
                            time.sleep(0.1)
                            arduino.write(b'BUZZ:PIT\n')
                            print("   🏁 Sent PIT NOW + buzzer to driver")
                        
                        elif msg_type == 'PIT_COUNTDOWN':
                            # Pit countdown
                            laps = content.get('laps', 0)
                            arduino.write(f'PIT_COUNTDOWN:{laps}\n'.encode())
                            print(f"   ⏱️  Sent pit countdown: {laps} laps")
                        
                        elif msg_type == 'STRATEGY':
                            # Regular strategy update - no buzz
                            message = content.get('message', 'Strategy update')
                            arduino.write(f'MSG:{message}\n'.encode())
                            print(f"   📊 Sent strategy: {message}")
                        
                        elif msg_type == 'LAP_UPDATE':
                            # Lap update
                            current = content.get('current_lap', 0)
                            total = content.get('total_laps', 78)
                            position = content.get('position', 'P1')
                            gap = content.get('gap', '+0.0')
                            arduino.write(f'LAP:{current}/{total}:{position}:{gap}\n'.encode())
                            print(f"   📍 Sent lap update: {current}/{total}")
                        
                        else:
                            # Generic message
                            message = content.get('message', str(content))
                            arduino.write(f'MSG:{message}\n'.encode())
                            print(f"   💬 Sent message: {message}")
                        
                        # Mark as acknowledged
                        supabase.table('driver_display')\
                            .update({'acknowledged': True})\
                            .eq('id', msg['id'])\
                            .execute()
                        
            except Exception as e:
                print(f"❌ Supabase error: {e}")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print(f"Driver Display stopped. Messages processed: {message_count}")
    print("="*60)
    arduino.close()

