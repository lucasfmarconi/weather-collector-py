#!/usr/bin/env bash
set -e

deploy_file() {
    local file=$1
    ampy ls lcd > /dev/null 2>&1 || ampy mkdir lcd
    ampy put "$file" "$file" && echo "  $file"
}

if [ -n "$1" ]; then
    echo "Deploying $1 to ESP32..."
    deploy_file "$1"
else
    echo "Deploying to ESP32..."

    # Ensure lcd directory exists on the board
    ampy ls lcd > /dev/null 2>&1 || ampy mkdir lcd

    ampy put config.py                                      && echo "  config.py"
    ampy put boot.py                                        && echo "  boot.py"
    ampy put main.py                                        && echo "  main.py"
    ampy put lcd/lcd_api.py lcd/lcd_api.py                  && echo "  lcd/lcd_api.py"
    ampy put lcd/machine_i2c_lcd.py lcd/machine_i2c_lcd.py && echo "  lcd/machine_i2c_lcd.py"
fi

echo "Done."
