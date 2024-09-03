import os  # I think it's better to use subprocess for this. but quick code for example
import time
import RPi.GPIO as GPIO # type: ignore           # import RPi.GPIO module  

code_status_led = None # SET THESE
code_error_led = None # SET THESE

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(code_status_led, GPIO.OUT)
GPIO.setup(code_error_led, GPIO.OUT)

while(1):
    status = os.system('systemctl is-active --quiet transmit.service')
    # print(status)  # will return 0 for active else inactive.
    print(f"Main Code running: {status == 0}")
    
    if status == 0:
        GPIO.output(code_status_led, 1)
        GPIO.output(code_error_led, 0)
        time.sleep(5)
    else:
        GPIO.output(code_status_led, 0)
        GPIO.output(code_error_led, 1)
        time.sleep(0.35)
        GPIO.output(code_error_led, 1)
        time.sleep(0.35)