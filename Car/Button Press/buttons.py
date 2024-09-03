#!/usr/bin/python

import RPi.GPIO as gpio # type: ignore
from subprocess import call
import time
from functions.start import start_service
from functions.stop import stop_service
from functions.restart import restart_now
from functions.shutdown import shutdown_now

Halt_other = False

# Start Button
button1_gpio_pin = None # SET THESE

# Restart Button
button2_gpio_pin = None # SET THESE

# Stop Button 
#   When Pressed with Start, Stops the code
#   When Pressed with Restart, PI shutsdown
button3_gpio_pin = None # SET THESE

# LED for Power
PowerLED = None # SET THESE


gpio.setmode(gpio.BCM)
gpio.setup(button1_gpio_pin, gpio.IN)
gpio.setup(button2_gpio_pin, gpio.IN)
gpio.setup(button3_gpio_pin, gpio.IN)
gpio.setup(PowerLED, gpio.OUT)

def start_code(channel):
    if not Halt_other:
        start_service()

def shutdown(channel):
    if not Halt_other:
        restart_now()

def stop_choice(channel):
    global Halt_other
    Halt_other = True
    if gpio.input(button1_gpio_pin) == gpio.HIGH:
        # If Stop button is pressed with Start button, stop the code
        stop_service()
        time.sleep(1)
        Halt_other = False
    elif gpio.input(button2_gpio_pin) == gpio.HIGH:
        # If Stop button is pressed with Restart button, shutdown the Pi
        shutdown_now()
        time.sleep(1)
        Halt_other = False
    
gpio.add_event_detect(button1_gpio_pin, gpio.RISING, callback=start_code, bouncetime=300)
gpio.add_event_detect(button2_gpio_pin, gpio.RISING, callback=shutdown, bouncetime=300)
gpio.add_event_detect(button3_gpio_pin, gpio.RISING, callback=stop_choice, bouncetime=300)

while 1:
    time.sleep(360)