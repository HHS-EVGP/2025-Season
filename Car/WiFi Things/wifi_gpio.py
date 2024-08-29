import RPi.GPIO as GPIO          # import RPi.GPIO module  
from sys import argv 
import time

wifi_status_led = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(wifi_status_led, GPIO.OUT)

while(1):
    # Check command line argument
    try:
        if len(argv) > 1:
            if argv[1] == 'up':
                GPIO.output(wifi_status_led, 1)
                print("GPIO set to HIGH")
            elif argv[1] == 'down':
                GPIO.output(wifi_status_led, 0)
                print("GPIO set to LOW")
            else:
                print("Invalid argument. Use 'up' or 'down'.")
        else:
            print("No argument provided.")
    except Exception as i:
        print(f"Error|: {i}")

    time.sleep(2.5)
