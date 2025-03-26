import busio # type: ignore
import serial # type: ignore
import RPi.GPIO as GPIO  # type: ignore
from adafruit_ads1x15.analog_in import AnalogIn # type: ignore
import board # type: ignore
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX # type: ignore
from adafruit_ads1x15.ads1115 import ADS # type: ignore

import math
import subprocess
import time
import logging
import struct

print("I guess all of the packages loaded! (:")

OnGPStime = False

# Transmission Variables
freq = 915 # Frequency in MHz
Pus = 10 # Duration of a 1 or 0 pulse in µs
Gus = 0 # Duration of gap between bits in µs
preamble = "1" * 128 

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
#B2 = AnalogIn(analogB, ADS.P2) # Port not used
B3 = AnalogIn(analogB, ADS.P3) # brake

#Setup UART for Cycle Anyalist
cycleAnalyst = serial.Serial('/dev/serial0',baudrate=9600)
#Setup variables
running = True
dataR = None
conter = 0

# Function to write to a specific SC18IM704 UART (Used only if needed by user)
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
    # Input from CA is: amp_hours|voltage|current|speed|miles 
    try:
        data = read_from_uart(CA704_ADDR, 10)  # Adjust length for Cycle Analyst
        if data:
            input = data.strip()
            amp_hours, voltage, current, speed, miles = input.split('|')
            return amp_hours, voltage, current, speed, miles
        else:
            amp_hours = voltage = current = speed = miles = float('-inf')
            return  amp_hours, voltage, current, speed, miles
    except Exception as e:
        print(f"Error in UART_CA function: {e}")
        return float('-inf')

# UART handler for GPS

def UART_GPS():
    # The GPS unit returns the same data in varius formats at once (by default)
    # The $GPRMC scheme containes the most relevant data
    # $GPRMC documentation: https://docs.novatel.com/OEM7/Content/Logs/GPRMC.htm
    try:
        data = read_from_uart(GPS704_ADDR, 128)  # GPS data length can be longer (up to 255 bytes)
        if data:

            input = data.strip()
            if "$GPRMC" in input:
                input = input.split("$GPGGA")[1]
                input = input.split("\r\n")[0]

                timestamp, pos_status, lat, lat_dir, lon, lon_dir, speed, track_true, date, \
                mag_var, var_dir, mod_ind, checksum = input.split(',')

                #If no GPS fix, return -inf for all variables
                if pos_status == 'V':
                    print("No GPS fix!!!")
                    GPS_x = GPS_y = GPS_z = float('-inf')
                    return GPS_x, GPS_y, GPS_z
                
                # Set System time to gps time if not done yet
                if OnGPStime == False:
                    # Extract hours, minutes, and seconds from timestamp
                    hours = timestamp[:2]
                    minutes = timestamp[2:4]
                    seconds = timestamp[4:]

                    # Extract day, month, and year from date
                    day = date[:2]
                    month = date[2:4]
                    year = 2000 + int(date[4:]) # Change this in 75 years; This is a limitation of the $GPRMC format

                    # Format the date and time for the `date` command
                    formatted_time = f"{year}-{month}-{day} {hours}:{minutes}:{seconds}"

                    # Set the system time using the `date` command
                    subprocess.run(["sudo date -s", formatted_time], check=True)
                    print("System time sucessfully set to GPS time:", formatted_time)

                    OnGPStime = True
                
                # Convert latitude and longitude to decimal degrees
                lat = float(lat[:2]) + float(lat[2:]) / 60.0
                if lat_dir == 'S':
                    lat = -lat

                lon = float(lon[:3]) + float(lon[3:]) / 60.0
                if lon_dir == 'W':
                    lon = -lon

                # Convert decimal degrees to radians
                lat = math.radians(lat)
                lon = math.radians(lon)

                # The IAU nominal "zero tide" equatorial radius of the Earth
                R = 6378100

                # Convert to Cartesian coordinates
                GPS_x = R * math.cos(lat) * math.cos(lon)
                GPS_y = R * math.cos(lat) * math.sin(lon)
                GPS_z = R * math.sin(lat)

                return GPS_x, GPS_y, GPS_z,
        
            else:
                print("No $GPRMC found")
                GPS_x = GPS_y = GPS_z = float('-inf')
                return GPS_x, GPS_y, GPS_z # Have to use system time instead of GPS time
                #return UART_GPS() # Restart the function
            
        else:
            GPS_x = GPS_y = GPS_z = float('-inf')
            return GPS_x, GPS_y, GPS_z
        
    except Exception as e:
        print(f"Error in UART_GPS function: {e}")
        GPS_x = GPS_y = GPS_z = float('-inf')
        return time.time(), GPS_x, GPS_y, GPS_z

def thermistor(idx):
    R2 = R1 * (1023.0 / float(idx) - 1.0)
    logR2 = math.log(R2)
    T = 1.0 / (c1 + c2 * logR2 + c3 * logR2**3)
    T = T - 273.15  # Convert from Kelvin to Celsius
    T = (T * 9.0) / 5.0 + 32.0  # Convert from Celsius to Fahrenheit
    return T

def analogPull():
    # Throttle Value
    try:
        throttle = A0.value
    except:
        throttle = float('-inf')

    # Brake Value
    try:
        brake = B3.value
    except:
        brake = float('-inf')

    # Motor Temperature
    try:
        motor_temp = A1.value
    except:
        motor_temp = float('-inf')

    # Battery 1 Temperature
    try:
        batt_1 = thermistor(A2.value)
    except:
        batt_1 = float('-inf')

    # Battery 2 Temperature
    try:
        batt_2 = thermistor(A3.value)
    except:
        batt_2 = float('-inf')

    # Battery 3 Temperature
    try:
        batt_3 = thermistor(B0.value)
    except:
        batt_3 = float('-inf')

    # Battery 4 Temperature
    try: 
        batt_4 = thermistor(B1.value)
    except:
        batt_4 = float('-inf')

    return throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4

def sendRF(data):
    GPIO.output(sendLED, 1)
    subprocess.run(["sudo ./sendook -0", Pus, "-1", Pus, "-g", Gus, "-f", freq, preamble, data]) # Uses GPIO 4 (Pin 7)
    print("Sent:", data,)

while running:
    #Get Data
    amp_hours, voltage, current, speed, miles = UART_CA()
    throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4 = analogPull()
    GPS_x, GPS_y, GPS_z = UART_GPS()

    #Format Data
    for var in [time.time(), amp_hours, voltage, current, speed, miles, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4, GPS_x, GPS_y, GPS_z]:
        bin_var = ''.join(f'{byte:08b}' for byte in struct.pack('>d', var)) # Encode float to 1s and 0s (64 bit)
        data_2_send += str(bin_var)

    #Send Data
    sendRF(data_2_send)

    #Log Data
    logging.warning(data_2_send)
    GPIO.output(sendLED, 0)
    time.sleep(0.25)