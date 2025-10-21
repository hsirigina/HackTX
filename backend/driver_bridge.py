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
    """Find Arduino serial port automatically - prefer 21301 which is the display"""
    ports = serial.tools.list_ports.comports()

    # First, try to find the specific display Arduino (port 21301)
    for port in ports:
        if '21301' in port.device:
            print(f"✅ Found display Arduino: {port.device}")
            return port.device

    # Otherwise, try any USB modem
    for port in ports:
        if 'usbserial' in port.device.lower() or 'usbmodem' in port.device.lower() or 'arduino' in port.description.lower():
            print(f"⚠️  Using Arduino port: {port.device}")
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
    print(f"   Port: {SERIAL_PORT}")
    print(f"   Baudrate: 9600")
    print(f"   Timeout: 1 second")
except serial.SerialException as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("DRIVER DISPLAY BRIDGE RUNNING")
print("="*60)
print("Polling Supabase for messages...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

# Test Arduino connection and set default ready message
print("🧪 TESTING ARDUINO CONNECTION...")
try:
    # Send default F1 DRIVER READY message
    ready_msg = "MSG:F1 DRIVER|READY\n"
    arduino.write(ready_msg.encode())
    arduino.flush()
    time.sleep(0.5)
    print(f"✅ Sent ready message to Arduino display")
except Exception as e:
    print(f"❌ Failed to send to Arduino: {e}")
print()

last_check = time.time()
last_message_id = 0
message_count = 0
POLL_INTERVAL = 1.0  # Check Supabase every second
poll_count = 0

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
                print(f"🔍 [BRIDGE→SUPABASE] Polling for new messages...")

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

                        print(f"\n{'='*70}")
                        print(f"📥 [SUPABASE→BRIDGE] Pulled message from Supabase:")
                        print(f"   Message #{message_count}")
                        print(f"   ID: {msg['id']}")
                        print(f"   Type: {msg_type}")
                        print(f"   Priority: {msg['priority']}")
                        print(f"   Content: {content}")

                        if msg_type == 'ENGINEER_ALERT':
                            # Engineer touched sensor
                            serial_cmd = 'ENGINEER_ALERT\n'
                            arduino.write(serial_cmd.encode())
                            print(f"📡 [BRIDGE→ARDUINO] Sent: {serial_cmd.strip()}")

                        elif msg_type == 'PIT_NOW':
                            # Pit stop - show message AND buzz
                            serial_cmd = 'PIT_NOW\n'
                            arduino.write(serial_cmd.encode())
                            print(f"📡 [BRIDGE→ARDUINO] Sent: {serial_cmd.strip()}")
                            time.sleep(0.1)
                            buzz_cmd = 'BUZZ:PIT\n'
                            arduino.write(buzz_cmd.encode())
                            print(f"📡 [BRIDGE→ARDUINO] Sent: {buzz_cmd.strip()}")

                        elif msg_type == 'PIT_COUNTDOWN':
                            # Pit countdown
                            laps = content.get('laps', 0)
                            serial_cmd = f'PIT_COUNTDOWN:{laps}\n'
                            arduino.write(serial_cmd.encode())
                            print(f"📡 [BRIDGE→ARDUINO] Sent: {serial_cmd.strip()}")

                        elif msg_type == 'STRATEGY':
                            # Regular strategy update - no buzz
                            message = content.get('message', 'Strategy update')
                            serial_cmd = f'MSG:{message}\n'

                            print(f"📡 [BRIDGE→ARDUINO] Sending: {serial_cmd.strip()}")
                            print(f"   Bytes to send: {serial_cmd.encode()}")
                            arduino.write(serial_cmd.encode())
                            arduino.flush()  # Force write to serial port
                            print(f"✅ [BRIDGE→ARDUINO] Write completed")

                            # Check for immediate Arduino response
                            print(f"👂 [BRIDGE] Listening for Arduino debug output...")
                            time.sleep(0.5)  # Give Arduino time to process
                            if arduino.in_waiting:
                                while arduino.in_waiting:
                                    response = arduino.readline().decode().strip()
                                    print(f"📟 [ARDUINO→BRIDGE] {response}")
                            else:
                                print(f"⚠️  [BRIDGE] No response from Arduino (in_waiting = {arduino.in_waiting})")

                            print(f"⏱️  Waiting 2 seconds for display update...")
                            time.sleep(1.5)

                        elif msg_type == 'LAP_UPDATE':
                            # Lap update
                            current = content.get('current_lap', 0)
                            total = content.get('total_laps', 78)
                            position = content.get('position', 'P1')
                            gap = content.get('gap', '+0.0')
                            serial_cmd = f'LAP:{current}/{total}:{position}:{gap}\n'
                            arduino.write(serial_cmd.encode())
                            print(f"📡 [BRIDGE→ARDUINO] Sent: {serial_cmd.strip()}")

                        else:
                            # Generic message
                            message = content.get('message', str(content))
                            serial_cmd = f'MSG:{message}\n'
                            arduino.write(serial_cmd.encode())
                            print(f"📡 [BRIDGE→ARDUINO] Sent: {serial_cmd.strip()}")

                        # Mark as acknowledged
                        print(f"✅ [BRIDGE→SUPABASE] Marking message ID {msg['id']} as acknowledged")
                        supabase.table('driver_display')\
                            .update({'acknowledged': True})\
                            .eq('id', msg['id'])\
                            .execute()
                        print(f"{'='*70}\n")
                    else:
                        print(f"   No new messages (last ID: {last_message_id})")
                else:
                    print(f"   No unacknowledged messages in queue")
                        
            except Exception as e:
                print(f"❌ Supabase error: {e}")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print(f"Driver Display stopped. Messages processed: {message_count}")
    print("="*60)
    arduino.close()

