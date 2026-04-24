#!/usr/bin/env bash
set -e

echo "Deploying to ESP32..."

# Ensure umqtt directory exists on the board
ampy ls umqtt > /dev/null 2>&1 || ampy mkdir umqtt

ampy put config.py       && echo "  config.py"
ampy put boot.py         && echo "  boot.py"
ampy put main.py         && echo "  main.py"
ampy put umqtt/simple.py umqtt/simple.py && echo "  umqtt/simple.py"

echo "Done."
