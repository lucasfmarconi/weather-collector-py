# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

import network
import esp
import gc
import config

gc.collect()
esp.osdebug(None)


def connect_wlan():
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


connect_wlan()
