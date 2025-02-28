import busio # type: ignore
import serial # type: ignore
import smbus # type: ignore

import RPi.GPIO as GPIO  # type: ignore
from adafruit_ads1x15.analog_in import AnalogIn # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX # type: ignore

import math
import subprocess
import time
import logging

print("I guess all of the packages loaded! (:")

# Make sure to replace with your schools ID (Whatever you want, just not the same as someone else)
school_id = "hhs"

#Transmission Variables
freq = 915 # Frequency in MHz
sendtimes = 1 # Number of times to send the message (For redundancy)

#Current values are as small as is possible
Zus = 12 # Pulse duration of bit 0 in µs
Ous = 13 # Pulse duration of bit 1 in µs
Gus = 11 # Duration of gap between bits in µs
Pus = 14 # Duration of pauses between messages in µs

#Setup Thermistor Values
R1 = 10000.0
logR2 = R2 = T = 0.0  # Initializing logR2, R2, and T as float values (defaulting to 0.0)
c1 = 1.009249522e-03
c2 = 2.378405444e-04
c3 = 2.019202697e-07

#Setup Send LED
sendLED = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(sendLED, GPIO.OUT)
GPIO.output(sendLED, 0)
#Setup i2C & Devices
i2c = busio.I2C(board.SCL, board.SDA)
analogA = ADS.ADS1115(i2c, address = 0x4A)
analogB = ADS.ADS1115(i2c, address = 0x4B)
CA704_ADDR = 0x28  # Replace with the actual I2C address -- Cycle Analyst
GPS704_ADDR = 0x29  # Replace with the actual I2C address -- GPS

# FOR SETTING UP 704', FOLLOW THIS GPT PAGE:
# https://chatgpt.com/share/673cbcb7-9a74-8010-9a24-c0a5603eb385

#Setup Analog In Ports
A0 = AnalogIn(analogA, ADS.P0) # throttle
A1 = AnalogIn(analogA, ADS.P1) # motorTemp
A2 = AnalogIn(analogA, ADS.P2) # battTemp1
A3 = AnalogIn(analogA, ADS.P3) # battTemp2
B0 = AnalogIn(analogB, ADS.P0) # battTemp3
B1 = AnalogIn(analogB, ADS.P1) # battTemp4
B2 = AnalogIn(analogB, ADS.P2) # ****What does this do???****
B3 = AnalogIn(analogB, ADS.P3) # brake
#Setup UART for Cycle Anyalist
cycleAnalyst = serial.Serial('/dev/serial0',baudrate=9600)
#Setup variables
running = True
dataR = None
conter = 0

# Function to write to a specific SC18IM704 UART
def write_to_uart(device_addr, data):
    try:
        # Command structure: Start ('S'), data, Stop ('P')
        command = [ord('S')] + list(data.encode('utf-8')) + [ord('P')]
        i2c.writeto(device_addr, bytearray(command))
        print(f"Sent to UART on device {device_addr:02X}: {data}")
    except Exception as e:
        print(f"Error writing to UART on device {device_addr:02X}: {e}")

# Function to read from a specific SC18IM704 UART
def read_from_uart(device_addr, length=10):
    try:
        # Command to read data from UART: 'S', I2C address, 'R', 'P'
        command = [ord('S'), 0x01, ord('R'), ord('P')]
        i2c.writeto(device_addr, bytearray(command))
        time.sleep(0.1)  # Allow time for processing
        response = i2c.readfrom(device_addr, length)  # Adjust length as needed
        print(f"Received from UART on device {device_addr:02X}: {response}")
        return response.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error reading from UART on device {device_addr:02X}: {e}")
        return None

# UART handler for Cycle Analyst
def UART_CA():
    # Send output as: "CA,amp_hours,voltage,current,speed,miles|"
    try:
        data = read_from_uart(CA704_ADDR, 10)  # Adjust length for Cycle Analyst
        if data:
            # Process Cycle Analyst data here
            return f"CA,{data.strip()}|"
        else:
            return "CA,None,None,None,None,None|"
    except Exception as e:
        print(f"Error in UART_CA function: {e}")
        return "CA,None,None,None,None,None|"

# UART handler for GPS
def UART_GPS():
    try:
        data = read_from_uart(GPS704_ADDR, 128)  # GPS data length can be longer
        if data:
            # Process GPS NMEA data here
            return f"GPS,{data.strip()}|"
        else:
            return "GPS,None|"
    except Exception as e:
        print(f"Error in UART_GPS function: {e}")
        return "GPS,None|"

def thermistor(idx):
    R2 = R1 * (1023.0 / float(idx) - 1.0)
    logR2 = math.log(R2)
    T = 1.0 / (c1 + c2 * logR2 + c3 * logR2**3)
    T = T - 273.15  # Convert from Kelvin to Celsius
    T = (T * 9.0) / 5.0 + 32.0  # Convert from Celsius to Fahrenheit
    return T

def analogPull():
    data = ""
    temp_data = ""

    # Throttle Value
    try:
        data += f"throttle,{A0.value}|"
    except:
        data += f"throttle,None|"

    # Brake Value
    try:
        data += f"brake,{B3.value}|"
    except:
        data += f"brake,None|"

    # Motor Temperature
    try:
        temp_data += f"{A1.value},"
    except:
        temp_data += "None,"

    # Battery 1 Temperature
    try:
        temp_data += f"{thermistor(A2.value)},"
    except:
        temp_data += "None,"

    # Battery 2 Temperature
    try:
        temp_data += f"{thermistor(A3.value)},"
    except:
        temp_data += "None,"

    # Battery 3 Temperature
    try:
        temp_data += f"{thermistor(B0.value)},"
    except:
        temp_data += "None,"

    # Battery 4 Temperature
    try:
        temp_data += f"{thermistor(B1.value)}"
    except:
        temp_data += "None"

    data += f"tempData,{temp_data}|"

    return data

def sendRF(data):
    GPIO.output(sendLED, 1)
    subprocess.run(["sudo ./sendook -0", Zus, "-1", Ous, "-g", Gus, "-p", Pus, "-f", freq, "-r", snedtimes, "01111110", data]) # 01111110 Is ASCII for ~ which is used to seperate messages
    print("Sent:", data,)

while running:

    data_2_send = f"{school_id}|" 
    data_2_send += analogPull()      # Analog sensor data
    data_2_send += UART_CA()         # Cycle Analyst data
    data_2_send += UART_GPS()        # GPS data

    bin_2_send = ' '.join(format(ord(char), '08b') for char in data_2_send) #Format strings into binary
    sendRF(bin_2_send)

    #Log Data
    logging.warning(data_2_send)
    GPIO.output(sendLED, 0)
    time.sleep(0.25)