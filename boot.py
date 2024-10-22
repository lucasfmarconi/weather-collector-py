# This file is executed on every boot (including wake-boot from deepsleep)

import network

# esp.osdebug(None)
# import webrepl
# webrepl.start()

import time
import esp
import gc
import config

gc.collect()
esp.osdebug(None)


def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        ssid = config.WIFI_SSID
        password = config.WIFI_PASSWORD
        print("Trying to connect to the network ", ssid)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.1)
            pass
    print("\nNetwork config: ", wlan.ifconfig())


connect_wlan()
