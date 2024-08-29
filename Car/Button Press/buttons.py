#!/usr/bin/python
#
#   backlight-toggle.py   10-25-2015 
#     
#   RPF 7" Touchscreen Display
#          Toggles backlight on/off with button press 
#          Uses GPIO5  (BOARD Pin 29)


import RPi.GPIO as gpio
from subprocess import call
import time
from start import start_service
from restart import restart_now

button1_gpio_pin = None # SET THESE
button2_gpio_pin = None # SET THESE

gpio.setmode(gpio.BCM)
gpio.setup(button1_gpio_pin, gpio.IN)
gpio.setup(button2_gpio_pin, gpio.IN)

def start_code(channel):
    start_service()

def shutdown(channel):
    restart_now()
    
gpio.add_event_detect(button1_gpio_pin, gpio.RISING, callback=start_code, bouncetime=300)
gpio.add_event_detect(button2_gpio_pin, gpio.RISING, callback=shutdown, bouncetime=300)

while 1:
    time.sleep(360)