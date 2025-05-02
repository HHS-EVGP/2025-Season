#!/usr/bin/env python3

import os
import time
import subprocess
from gpiozero import LED, Button #type: ignore
from signal import pause
import sys

import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - SM - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


logging.info("Starting script.")

# LED setup
green_led = LED(17)  # Script running
white_led = LED(22)  # PI has power
red_led = LED(4)     # Script failed

# Button setup
stop_btn = Button(19)    # STOP script
start_btn = Button(13)   # START script
restart_btn = Button(26) # RESTART PI

# Path configuration
SCRIPT_PATH = "/home/car/collector.py"
VENV_ACTIVATE = "/home/car/pyenv/bin/activate"
process = None

def start_script():
    logging.info("Start Button")
    global process
    if process is None or process.poll() is not None:
        try:
            # Command to start script in virtual environment
            # source pyenv/bin/activate && python3 collector.py
            command = f"source {VENV_ACTIVATE} && python3 {SCRIPT_PATH}"
            #command = f"python3 {SCRIPT_PATH}"

            process = subprocess.Popen(
                command,
                shell=True,
                executable='/bin/bash',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            red_led.off()
            for i in range(4):
                green_led.off()
                time.sleep(0.1)
                green_led.on()
                time.sleep(0.1)
            logging.info("Started with Button")
            print("Script started successfully in virtual environment")
        except Exception as e:
            red_led.on()
            green_led.off()
            logging.info("Failed to start with button")
            print(f"Failed to start script: {e}")

def stop_script():
    logging.info("Stop Button")
    global process
    if process and process.poll() is None:
        for ii in range(4):
            green_led.on()
            red_led.on()
            time.sleep(0.1)
            green_led.off()
            red_led.off()
            time.sleep(0.1)
        # Send SIGTERM to entire process group
        os.killpg(os.getpgid(process.pid), 15)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(process.pid), 9)
        logging.info("Script stoped with button")
        print("Script stopped")

def restart_pi():
    logging.info("Restarting PI from buttons")
    print("Initiating system restart...")
    for i in range(10):
        green_led.on()
        red_led.on()
        white_led.on()
        time.sleep(0.15)
        green_led.off()
        red_led.off()
        white_led.off()
        time.sleep(0.15)
    os.system("sudo reboot")

def monitor_script():
    while True:
        if process and process.poll() is not None:
            # Script has terminated
            green_led.off()
            if process.returncode != 0:  # If script exited with error
                red_led.on()
                #print("Script has stopped or failed")
        else:
            red_led.off()

        time.sleep(1)

if __name__ == "__main__":
    # Turn on power indicator
    white_led.on()

    # Set up button actions
    start_btn.when_pressed = start_script
    stop_btn.when_pressed = stop_script
    restart_btn.when_pressed = restart_pi

    # Start the script automatically on boot
    # start_script()

    # Monitor script status
    try:
        monitor_script()
    except KeyboardInterrupt:
        stop_script()
        white_led.off()