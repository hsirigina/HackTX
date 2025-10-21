#!/usr/bin/env python3
"""Quick script to reset Arduino display"""
import serial
import time

port = '/dev/tty.usbmodem21301'
print(f"Connecting to {port}...")
arduino = serial.Serial(port, 9600, timeout=1)
time.sleep(2)  # Wait for Arduino reset

print("Sending CLEAR command...")
arduino.write(b'CLEAR\n')
time.sleep(0.5)

print("Sending test message...")
arduino.write(b'MSG:System Ready\n')
time.sleep(0.5)

# Read response
while arduino.in_waiting:
    print(f"Arduino: {arduino.readline().decode().strip()}")

arduino.close()
print("✅ Arduino reset complete!")
