#!/bin/bash

# The interface you want to monitor, e.g., wlan0
INTERFACE="wlan0"

# Previous state of the WiFi connection
PREV_STATE="down"

while true; do
    # Check if connected to WiFi
    if iwconfig $INTERFACE | grep -q "ESSID:off/any"; then
        STATE="down"
    else
        STATE="up"
    fi

    # If the state has changed, update the GPIO
    if [ "$STATE" != "$PREV_STATE" ]; then
        python3 ./wifi_gpio.py $STATE
        PREV_STATE=$STATE
    fi

    # Check every 10 seconds (adjust as needed)
    sleep 10
done
