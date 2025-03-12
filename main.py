# main.py
import machine
import time
import dht
import config
from umqtt.simple import MQTTClient
import ssl

# region Initialisation
led = machine.Pin(2, machine.Pin.OUT)
dht_pin = dht.DHT11(machine.Pin(17))
LOOP_TIME = config.LOOP_TIME
DHT11_WAIT_TIME = config.DHT11_WAIT_TIME
# endregion

def blink_led():
    print("Blinking LED")
    led.value(1)  # Turn the LED on
    time.sleep(5)
    led.value(0)  # Turn the LED off

# region DHT11
def read_dht11():
    print("Measuring T and H with DHT11")
    time.sleep(DHT11_WAIT_TIME)  # Initial delay to ensure the sensor is ready
    try:
        dht_pin.measure()
        temperature = dht_pin.temperature()
        humidity = dht_pin.humidity()

        publish_temperature(temperature)
        publish_humidity(humidity)

        print("Temperature: {}°C, Humidity: {}%".format(temperature, humidity))
    except OSError as e:
        print("Failed to read DHT sensor:", e)

# endregion


# region MQTT
def publish_humidity(humidity):
    humidity_topic = config.MQTT_TOPIC_PUB + "/humidity"
    print("Publishing to topic:", humidity_topic)
    mqtt_client.publish(humidity_topic, bytes(str(humidity), "utf-8"))


def publish_temperature(temperature):
    temperature_topic = config.MQTT_TOPIC_PUB + "/temperature"
    print("Publishing to topic:", temperature_topic)
    mqtt_client.publish(temperature_topic, bytes(str(temperature), "utf-8"))


def process_control_message(topic, msg):
    print("Received message:", (topic, msg))
    if "restart" in msg:
        restart()
    elif "blink" in msg:
        blink_led()
    elif "airsensor-read" in msg:
        read_dht11()
    elif "change-loop-time" in msg:
        update_loop_time(msg)
    elif "change-dht-read-time" in msg:
        update_dht_read_time(msg)
    else:
        print("Unknown message on topic {} msg: {}".format(topic, msg))


def update_loop_time(msg):
    global LOOP_TIME
    LOOP_TIME = int(msg)
    print("Changed loop time to:", config.LOOP_TIME)


def update_dht_read_time(msg):
    global DHT11_WAIT_TIME
    DHT11_WAIT_TIME = int(msg)
    print("Changed loop time to:", config.DHT11_WAIT_TIME)


def connect_to_mqtt_broker():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.verify_mode = ssl.CERT_NONE

    mqtt_client = MQTTClient(
        config.MQTT_CLIENT_ID,
        config.MQTT_SERVER,
        user=config.MQTT_USER,
        password=config.MQTT_PASS,
        ssl=ssl_context,
    )

    mqtt_client.set_last_will(
        "lwt/machines/mpy-esp32", "Machine is offline", retain=True
    )

    mqtt_client.connect()
    return mqtt_client


def restart():
    time.sleep(10)
    print("Restarting machine...")
    machine.reset()


def subscribe_to_machine_control_topic():
    print("Subscribing to machine control topic:", config.MQTT_TOPIC_SUB)
    mqtt_client.set_callback(process_control_message)
    mqtt_client.subscribe(config.MQTT_TOPIC_SUB)


try:
    print("\nStarting MQTT Client...")
    mqtt_client = connect_to_mqtt_broker()
    subscribe_to_machine_control_topic()
except OSError as e:
    print("Failed to connect to MQTT broker")
    restart()

# endregion

while True:
    print("\nMain loop started...")
    try:
        received_message = mqtt_client.check_msg()
        if received_message is not None:
            print("Received pending message during startup:", received_message)
        blink_led()
        read_dht11()
        time.sleep(config.LOOP_TIME)
    except OSError as e:
        restart()
