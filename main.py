# main.py
import machine
import time
import dht
import config
from umqtt.simple import MQTTClient
import ssl
from machine import Pin, SoftI2C
from lcd.machine_i2c_lcd import I2cLcd

# region Initialisation

# region I2c LCD
# Define the I2C LCD address and dimensions
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# Initialize I2C and LCD objects
lcd = None
try:
    print("I2c LCD init...")
    i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)

    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    print("I2c LCD initializated...")
    time.sleep(2)
    lcd.clear()

    lcd.putstr("Initializing station...")
    time.sleep(2)
except Exception as e:
    print("I2c LCD init failed:", e)

# endregion

led = machine.Pin(2, machine.Pin.OUT)
dht_pin = dht.DHT11(machine.Pin(17))
LOOP_TIME = config.LOOP_TIME
DHT11_WAIT_TIME = config.DHT11_WAIT_TIME
TZ_OFFSET = -3 * 3600  # UTC-3 Brasília / São Paulo
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

        publish_last_read()
        lcd_write_sensor_data(temperature, humidity)
        print("Temperature: {}°C, Humidity: {}%".format(temperature, humidity))
    except OSError as e:
        print("Failed to read DHT sensor:", e)

# endregion


# region MQTT


def publish_humidity(humidity):
    humidity_topic = config.MQTT_TOPIC_PUB + "/dht11/humidity"
    print("Publishing to topic:", humidity_topic)
    mqtt_client.publish(humidity_topic, bytes(str(humidity), "utf-8"))


def publish_temperature(temperature):
    temperature_topic = config.MQTT_TOPIC_PUB + "/dht11/temperature"
    print("Publishing to topic:", temperature_topic)
    mqtt_client.publish(temperature_topic, bytes(str(temperature), "utf-8"))


def publish_last_read():
    last_read_topic = config.MQTT_TOPIC_PUB + "/dht11/data-timestamp"
    print("Publishing to topic:", last_read_topic)
    t = time.gmtime()
    timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )
    mqtt_client.publish(last_read_topic, bytes(str(timestamp), "utf-8"))


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
        config.MQTT_TOPIC_PUB + "/status",
        "ESP32 board abruptly disconnected",
        retain=True,
    )

    mqtt_client.connect()
    mqtt_client.publish(
        config.MQTT_TOPIC_PUB + "/status",
        "online",
        retain=True,
    )
    return mqtt_client


def restart():
    time.sleep(10)
    print("Restarting machine...")
    try:
        mqtt_client.publish(
            config.MQTT_TOPIC_PUB + "/status",
            "offline",
            retain=True,
        )
        mqtt_client.disconnect()
    except Exception:
        pass
    machine.reset()


def subscribe_to_machine_control_topic():
    msg = "Subscribing to machine control topic: " + config.MQTT_TOPIC_DEVICES_SUB
    print(msg)
    mqtt_client.set_callback(process_control_message)
    mqtt_client.subscribe(config.MQTT_TOPIC_DEVICES_SUB + "/control/#")


def lcd_write_sensor_data(temperature, humidity):
    if lcd is None:
        return
    t = time.gmtime(time.time() + TZ_OFFSET)
    time_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
    line1 = "T:{}C | H:{}%".format(temperature, humidity)
    line2 = "Last: " + time_str
    lcd.clear()
    lcd.putstr(line1)
    lcd.move_to(0, 1)
    lcd.putstr(line2)
    lcd.blink_cursor_on()


def lcd_clear_and_write(msg):
    if lcd is None:
        return
    lcd.blink_cursor_on()
    lcd.clear()
    lcd.putstr(msg)


def lcd_write_fullpage(line1, line2):
    if lcd is None:
        return
    lcd.clear()
    lcd.putstr(line1)
    lcd.move_to(0, 1)
    lcd.putstr(line2)
    lcd.blink_cursor_on()


try:
    print("\nStarting MQTT Client...")
    lcd_clear_and_write("Connecting to MQTT...")
    mqtt_client = connect_to_mqtt_broker()
    lcd_write_fullpage("MQTT Connected!", "Station init...")
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
