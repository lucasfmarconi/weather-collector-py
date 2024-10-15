# main.py
import machine
import time
import dht
import network
import config

# Initialize pin 2 (usually the built-in LED on ESP32)
led = machine.Pin(2, machine.Pin.OUT)
dht_pin = dht.DHT11(machine.Pin(17))


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    # wlan.config(ssid="ESP32 Weather Collector", channel=11)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        ssid = config.WIFI_SSID
        password = config.WIFI_PASSWORD
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print(wlan.status())
            print("Trying to connect to the network {}...", ssid)
            pass
    print("network config:", wlan.ifconfig())


def blink_led():
    print("Blinking LED")
    led.value(1)  # Turn the LED on
    time.sleep(5)  # Wait for 5 seconds
    led.value(0)  # Turn the LED off
    time.sleep(1)  # Wait for 1 second


def read_dht11():
    print("Measuring T and H with DHT11")
    time.sleep(15)  # Initial delay to ensure the sensor is ready
    try:
        dht_pin.measure()
        temperature = dht_pin.temperature()
        humidity = dht_pin.humidity()
        print("Temperature: {}°C, Humidity: {}%".format(temperature, humidity))
    except OSError as e:
        print("Failed to read sensor:", e)


while True:
    blink_led()
    do_connect()
    read_dht11()
    time.sleep(2)  # Wait for 2 seconds before the next loop iteration
