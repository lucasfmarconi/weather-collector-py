# Weather Collector

MicroPython firmware for an ESP32 that collects temperature and humidity with a DHT11 sensor and publishes the readings to an MQTT broker over TLS. It shows the latest reading on a 16×2 I2C LCD and listens for control messages to restart the board, blink the LED, force a reading, or change timing parameters.

## Requirements

- ESP32 microcontroller running MicroPython
- DHT11 sensor
- 16×2 HD44780 LCD with a PCF8574 I2C backpack (optional — the firmware keeps running if it is missing)
- MQTT broker (TLS)
- Wi-Fi network

## Project layout

| Path | Role |
|------|------|
| `boot.py` | Runs on every boot: connects to Wi-Fi and syncs the clock via NTP |
| `main.py` | Application: LCD, DHT11, MQTT publish/subscribe, main loop |
| `config.py` | Wi-Fi/MQTT credentials and timings (git-ignored, create it yourself) |
| `lcd/` | Vendored HD44780/I2C driver ([dhylands/python_lcd](https://github.com/dhylands/python_lcd)) |
| `umqtt/simple.py` | MQTT client library (git-ignored, copy it from MicroPython's `umqtt.simple`) |
| `deploy.sh` | Uploads the files to the board with `ampy` |
| `.ampy` | Serial port settings used by `ampy` |

## Configuration

Create a `config.py` in the project root (it is git-ignored) with your Wi-Fi and MQTT broker details:

```python
WIFI_SSID = "Your_WiFi_SSID"
WIFI_PASSWORD = "Your_WiFi_Password"
MQTT_USER = "Your_MQTT_User"
MQTT_PASS = "Your_MQTT_Password"
MQTT_SERVER = "Your_MQTT_Server"
MQTT_CLIENT_ID = "Your_MQTT_Client_ID"
MQTT_TOPIC_PUB = "sensors/air-sensors/dht11"
MQTT_TOPIC_DEVICES_SUB = "devices/weather-collector"
LOOP_TIME = 10
DHT11_WAIT_TIME = 15
```

| Key | Description |
|-----|-------------|
| `MQTT_TOPIC_PUB` | Base topic for published data and status |
| `MQTT_TOPIC_DEVICES_SUB` | Base topic for control; the board subscribes to `<MQTT_TOPIC_DEVICES_SUB>/control/#` |
| `LOOP_TIME` | Seconds to sleep at the end of each main-loop iteration |
| `DHT11_WAIT_TIME` | Seconds to wait before each DHT11 measurement |

The local timezone used for the LCD clock is set by `TZ_OFFSET` in `main.py` (default UTC-3).

## Usage

1. Wire the sensor, LCD and LED as described in [Wiring / Pinout](#wiring--pinout).
2. Create `config.py` as described above.
3. Set up the host tooling and deploy:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   ./deploy.sh              # upload everything
   ./deploy.sh main.py      # or upload a single file
   ```
   `deploy.sh` uploads `config.py`, `boot.py`, `main.py` and the `lcd/` driver (creating `lcd/` on the board if needed). `umqtt/simple.py` is not uploaded by the script; put it on the board once with:
   ```sh
   ampy mkdir umqtt
   ampy put umqtt/simple.py umqtt/simple.py
   ```
4. The board connects to Wi-Fi, syncs the time over NTP, connects to the MQTT broker and starts publishing.
5. Control the board by publishing messages to the control topic.

## MQTT topics

With `MQTT_TOPIC_PUB` as the base topic, the board publishes:

| Topic | Payload |
|-------|---------|
| `<base>/dht11/temperature` | Temperature in °C |
| `<base>/dht11/humidity` | Relative humidity in % |
| `<base>/dht11/data-timestamp` | UTC time of the reading, ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`) |
| `<base>/status` | `online` on connect, `offline` on a clean restart (retained). If the board drops unexpectedly, the broker publishes the last-will message `ESP32 board abruptly disconnected`. |

## MQTT Control Messages

The board subscribes to `<MQTT_TOPIC_DEVICES_SUB>/control/#`. The command is read from the message **payload**; the subtopic is not used.

- `restart`: Restarts the ESP32 (publishes `offline` first).
- `blink`: Blinks the onboard LED.
- `airsensor-read`: Reads the DHT11 sensor and publishes the data.
- `change-loop-time`: Changes the loop time interval.
- `change-dht-read-time`: Changes the DHT11 sensor read time interval.

> **Note:** messages are only processed when the main loop calls `check_msg()`, once per iteration. Each iteration includes the LED blink (5 s), the DHT11 wait and `LOOP_TIME`, so expect a delay before a command is handled.

### Known limitations

- `change-loop-time` and `change-dht-read-time` convert the payload straight to an integer, so the payload cannot both name the command and carry the value yet.
- `change-loop-time` updates the in-memory `LOOP_TIME`, but the main loop still sleeps for `config.LOOP_TIME`.

## Wiring / Pinout

### DHT11 Sensor → ESP32

| DHT11 Pin | ESP32 Pin  | Notes          |
|-----------|------------|----------------|
| VCC       | 3.3V       | Power          |
| GND       | GND        | Ground         |
| DATA      | GPIO 17    | Digital signal |

### I2C LCD (16×2) → ESP32

| LCD Pin | ESP32 Pin | Notes                          |
|---------|-----------|--------------------------------|
| VCC     | 5V        | Power                          |
| GND     | GND       | Ground                         |
| SDA     | GPIO 21   | I2C data (SoftI2C)             |
| SCL     | GPIO 22   | I2C clock (SoftI2C)            |

> **LCD I2C address:** `0x27`

### Onboard LED

| Function    | ESP32 Pin |
|-------------|-----------|
| Status LED  | GPIO 2    |

---

## Extra
### Working with ESP32 board and MicroPython
* Working with a Serial board connected
  * Follow serial output: `screen /dev/tty.usbserial-0001 115200`
  * Kill a dangling `screen` process: `screen -ls`, then `screen -XS PROCESS_NUM quit`

### Using ampy commands

[Ampy](https://github.com/scientific-python/adafruit-ampy) is a tool to interact with a MicroPython board over a serial connection. The serial port, baud rate and delay are read from the `.ampy` file in the project root (`AMPY_PORT`, `AMPY_BAUD`, `AMPY_DELAY`). On macOS, if you get "Could not enter raw repl", try `AMPY_DELAY=2.0` and lower from there. Pass `--port` to override the port. Some useful commands:

- **List files on the board:**
  ```sh
  ampy ls
  ```

- **Upload a file to the board:**
  ```sh
  ampy put main.py
  ```

- **Download a file from the board:**
  ```sh
  ampy get boot.py
  ```

- **Run a script on the board:**
  ```sh
  ampy run main.py
  ```

- **Remove a file from the board:**
  ```sh
  ampy rm main.py
  ```

## License

This project is licensed under the MIT License.
