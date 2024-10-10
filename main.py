# main.py
import machine
import time

# Initialize pin 2 (usually the built-in LED on ESP32)
led = machine.Pin(2, machine.Pin.OUT)

while True:
    led.value(1)  # Turn the LED on
    time.sleep(1)  # Wait for 1 second
    led.value(0)  # Turn the LED off
    time.sleep(1)  # Wait for 1 second
