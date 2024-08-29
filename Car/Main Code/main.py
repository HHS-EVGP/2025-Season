import adafruit_ads1x15.ads1115 as ADS
import adafruit_rfm9x
import board
import busio
import os
import time
import serial
import logging
import RPi.GPIO as GPIO 
from adafruit_ads1x15.analog_in import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX

print("I guess all of the packages loaded! (:")

# Make sure to replace with your schools ID (Whatever you want, just not the same as someone else)
school_id = "hhs"

#Setup Send LED
sendLED = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(sendLED, GPIO.OUT)
GPIO.output(sendLED, 0)
#Setup & Configure RFM9x LoRa Radio
rfm9x = adafruit_rfm9x.RFM9x(busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO), DigitalInOut(board.CE1), DigitalInOut(board.D25), 433.0, high_power = True)
rfm9x.tx_power = 23
#Setup i2C & Devices
i2c = busio.I2C(board.SCL, board.SDA)
analogA = ADS.ADS1115(i2c, address = 0x4A)
analogB = ADS.ADS1115(i2c, address = 0x4B)
imu = LSM6DSOX(i2c, address = 0x6A)
#Setup Analog In Ports
A0 = AnalogIn(analogA, ADS.P0) # throttle
A1 = AnalogIn(analogA, ADS.P1) # motorTemp
A2 = AnalogIn(analogA, ADS.P2) # battTemp1
A3 = AnalogIn(analogA, ADS.P3) # battTemp2
B0 = AnalogIn(analogB, ADS.P0) # battTemp3
B1 = AnalogIn(analogB, ADS.P1) # battTemp4
B2 = AnalogIn(analogB, ADS.P2) # 
B3 = AnalogIn(analogB, ADS.P3) # brake
#Setup UART for Cycle Anyalist
cycleAnalyst = serial.Serial('/dev/serial0',baudrate=9600)
#Setup variables
running = True
dataR = None
conter = 0
#Setup Logging
index = 1
while os.path.exists(f"/home/car/logs/{index:03}.data.log"):
    index += 1
new_file_name = f"/home/car/logs/{index:03}.data.log"
logging.basicConfig(filename=new_file_name, filemode='w', format='%(message)s')

def UART():
    # Send output as: "CA,amp_hours,voltage,current,speed,miles|"
    data = cycleAnalyst.read(10) # NEEDS WORK TODO
    print(bytes)
    print(data)
    return f"CA,None,None,None,None,None|"

def analogPull():
    data = ""
    temp_data = ""
    try:
        data += f"throttle,{A0.value}|"
    except:
        data += f"throttle,None|"

    # Motor Temperature
    try:
        temp_data += f"{A1.value},"
    except:
        temp_data += "None,"

    # Battery 1 Temperature
    try:
        temp_data += f"{A2.value},"
    except:
        temp_data += "None,"

    # Battery 2 Temperature
    try:
        temp_data += f"{A3.value},"
    except:
        temp_data += "None,"

    # Battery 3 Temperature
    try:
        temp_data += f"{B0.value},"
    except:
        temp_data += "None,"

    # Battery 4 Temperature
    try:
        temp_data += f"{B1.value}"
    except:
        temp_data += "None"

    data += f"tempData,{temp_data}|"

    try:
        data += f"brake,{B3.value}|"
    except:
        data += f"brake,None|"

    return data

def sendRF(data):
    GPIO.output(sendLED, 1)
    print(data)
    rfm9x.send(bytearray(data,'utf-8'))
    logging.warning(data)

while running:

    data_2_send = f"{school_id}|" 
    data_2_send += analogPull()
    data_2_send += UART()
    
    sendRF(data_2_send)
    GPIO.output(sendLED, 0)
    time.sleep(0.25)
