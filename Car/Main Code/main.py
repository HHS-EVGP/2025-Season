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
# Known id's: "hhs", "rhs"
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
A0 = AnalogIn(analogA, ADS.P0) # motorTemp
A1 = AnalogIn(analogA, ADS.P1) # throttle
A2 = AnalogIn(analogA, ADS.P2) # brake
A3 = AnalogIn(analogA, ADS.P3) # battTemp1
B0 = AnalogIn(analogB, ADS.P0) # 
B1 = AnalogIn(analogB, ADS.P1) # 
B2 = AnalogIn(analogB, ADS.P2) # 
B3 = AnalogIn(analogB, ADS.P3) # 
#Setup UART for Cycle Anyalist
cycleAnalyst = serial.Serial('/dev/serial0',baudrate=9600)
#Setup variables
running = True
dataR = None
conter = 0
#Setup Logging
index = 1
while os.path.exists(f"/home/car/{index}.data.log"):
    index = index + 1
new_file_name = f"/home/car/{index}.data.log"
logging.basicConfig(filename=new_file_name, filemode='w', format='%(message)s')

def imuPull():
    try:
        data = (
                str(round(imu.acceleration[0],2))
                +","+
                str(round(imu.acceleration[1],2))
                +","+
                str(round(imu.acceleration[2],2))
                +","+
                str(round(imu.gyro[0],2))
                +","+
                str(round(imu.gyro[1],2))
                +","+
                str(round(imu.gyro[2],2))
                )
        return f"imu,{data}|"
    except:
        return f"imu,None,None,None,None,None,None|"

def UART():
    # Send output as: "CA,amp_hours,voltage,current,speed,miles|"
    # data = cycleAnalyst.read(10)
    # print(bytes)
    # print(data)
    return f"CA,None,None,None,None,None|"

def analogPull():
    data = ""
    temp_data = ""
    try:
        data += f"throttle,{A1.value}|"
    except:
        data += f"throttle,None|"

    try:
        data += f"brake,{A2.value}|"
    except:
        data += f"brake,None|"

    # Motor Temperature
    try:
        temp_data += f"{A0.value},"
    except:
        temp_data += "None,"

    # Battery 1 Temperature
    try:
        temp_data += f"{A3.value},"
    except:
        temp_data += "None,"

    # Battery 2 Temperature
    try:
        temp_data += f"{B0.value}"
    except:
        temp_data += "None"

    data += f"tempatureData,{temp_data}|"

    return data

def sendRF(data):
    GPIO.output(sendLED, 1)
    print(data)
    rfm9x.send(bytearray(data,'utf-8'))
    logging.warning(data)

while running:

    data_2_send = f"{school_id}|" 
    data_2_send += analogPull()
    data_2_send += imuPull()
    data_2_send += UART()
    
    sendRF(data_2_send)
    GPIO.output(sendLED, 0)
    time.sleep(0.25)
