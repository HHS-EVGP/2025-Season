#!/usr/bin/python

import RPi.GPIO as gpio # type: ignore
from subprocess import subprocess
import time


# Functions
def restart_now():
    # Command to restart the Raspberry Pi
    restart_command = ["sudo reboot"]

    # Execute the restart command
    subprocess.run(restart_command, check=True)

def shutdown_now():
    # Command to restart the Raspberry Pi
    restart_command = ["sudo reboot"]

    # Execute the restart command
    subprocess.run(restart_command, check=True)

def start_service(service_name):
    try:
        # Starting the service
        subprocess.run(["sudo systemctl start", service_name], check=True)
        print(f"{service_name} successfully started.")
    except subprocess.CalledProcessError as e:
        # An error occurred while trying to start the service
        print(f"Failed to start {service_name}: {e}")

def stop_service(service_name):
    try:
        # Starting the service
        subprocess.run(["sudo systemctl stop", service_name], check=True)
        print(f"{service_name} successfully started.")
    except subprocess.CalledProcessError as e:
        # An error occurred while trying to start the service
        print(f"Failed to stop {service_name}: {e}")

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