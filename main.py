# main.py
import machine
import time
import dht
import config
from umqtt import MQTTClient

# region Initialisation
led = machine.Pin(2, machine.Pin.OUT)
dht_pin = dht.DHT11(machine.Pin(17))
# endregion

def blink_led():
    print("Blinking LED")
    led.value(1)  # Turn the LED on
    time.sleep(5)  # Wait for 5 seconds
    led.value(0)  # Turn the LED off
    time.sleep(1)  # Wait for 1 second

# region DHT11
def read_dht11():
    print("Measuring T and H with DHT11")
    time.sleep(15)  # Initial delay to ensure the sensor is ready
    try:
        dht_pin.measure()
        temperature = dht_pin.temperature()
        humidity = dht_pin.humidity()

        temperature_topic = config.MQTT_TOPIC_PUB + "/temperature"
        print("Publishing to topic:", temperature_topic)
        client.publish(temperature_topic, bytes(str(temperature), "utf-8"))

        humidity_topic = config.MQTT_TOPIC_PUB + "/humidity"
        print("Publishing to topic:", humidity_topic)
        client.publish(humidity_topic, bytes(str(humidity), "utf-8"))

        print("Temperature: {}°C, Humidity: {}%".format(temperature, humidity))
    except OSError as e:
        print("Failed to read sensor:", e)
# endregion


# region MQTT
def sub_cb(topic, msg):
    print((topic, msg))


def connect_and_subscribe():
    client = MQTTClient(
        config.MQTT_CLIENT_ID,
        config.MQTT_SERVER,
        user=config.MQTT_USER,
        password=config.MQTT_PASS,
    )
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(config.MQTT_TOPIC_SUB)
    print(
        "Connected to %s MQTT broker, subscribed to %s topic"
        % (config.MQTT_SERVER, config.MQTT_TOPIC_SUB)
    )
    return client


def restart_and_reconnect():
    print("Failed to connect to MQTT broker. Reconnecting...")
    time.sleep(10)
    machine.reset()


try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

# endregion

while True:
    try:
        new_message = client.check_msg()
        if new_message is not None:
            print("Received message:", new_message)
        blink_led()
        read_dht11()
        time.sleep(1)  # Wait for X seconds before the next loop iteration
    except OSError as e:
        restart_and_reconnect()
