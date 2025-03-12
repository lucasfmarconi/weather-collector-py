# Weather Collector

This project collects temperature and humidity data using a DHT11 sensor and publishes it to an MQTT broker. It also listens for control messages to perform various actions such as restarting, blinking an LED, or changing configuration parameters.

## Requirements

- ESP32 microcontroller
- DHT11 sensor
- MQTT broker
- Wi-Fi network

## Configuration

Update the `config.py` file with your Wi-Fi and MQTT broker details.

```python
WIFI_SSID = "Your_WiFi_SSID"
WIFI_PASSWORD = "Your_WiFi_Password"
MQTT_USER = "Your_MQTT_User"
MQTT_PASS = "Your_MQTT_Password"
MQTT_SERVER = "Your_MQTT_Server"
MQTT_CLIENT_ID = "Your_MQTT_Client_ID"
MQTT_TOPIC_PUB = "sensors/air-sensors/dht11"
MQTT_TOPIC_SUB = "devices/weather-collector/control/#"
LOOP_TIME = 10
DHT11_WAIT_TIME = 15
```

## Usage

1. Connect the DHT11 sensor to the ESP32.
2. Flash the `main.py` script to the ESP32.
3. The ESP32 will connect to the Wi-Fi and MQTT broker, and start publishing temperature and humidity data.
4. Control the ESP32 by publishing messages to the subscribed MQTT topic.

## MQTT Control Messages

- `restart`: Restarts the ESP32.
- `blink`: Blinks the onboard LED.
- `airsensor-read`: Reads the DHT11 sensor and publishes the data.
- `change-loop-time`: Changes the loop time interval.
- `change-dht-read-time`: Changes the DHT11 sensor read time interval.

## Example

To change the loop time to 20 seconds, publish the following message to the control topic:

```json
{
  "topic": "devices/weather-collector/control/change-loop-time",
  "message": "20"
}
```

## Extra
### Working with ESP32 board and MicroPython
* Working with a Serial board connected
  * Follow serial output: screen /dev/tty.usbserial-0001 115200
  * Kill a dangling `screen` process: screen -ls
                                      screen -XS PROCESS_NUM quit
* 
### Using ampy commands

Ampy is a tool to interact with a MicroPython board over a serial connection. Here are some useful commands:

- **List files on the board:**
  ```sh
  ampy --port /dev/ttyUSB0 ls
  ```

- **Upload a file to the board:**
  ```sh
  ampy --port /dev/ttyUSB0 put main.py
  ```

- **Download a file from the board:**
  ```sh
  ampy --port /dev/ttyUSB0 get boot.py
  ```

- **Run a script on the board:**
  ```sh
  ampy --port /dev/ttyUSB0 run main.py
  ```

- **Remove a file from the board:**
  ```sh
  ampy --port /dev/ttyUSB0 rm main.py
  ```

## License

This project is licensed under the MIT License.