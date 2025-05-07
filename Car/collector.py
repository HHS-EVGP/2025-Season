import busio # type: ignore
import serial # type: ignore
import RPi.GPIO as GPIO  # type: ignore
from adafruit_ads1x15.analog_in import AnalogIn # type: ignore
import board # type: ignore
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX # type: ignore
import adafruit_ads1x15.ads1115 as ADS # type: ignore
import adafruit_rfm9x # type: ignore

from cc1101 import CC1101 # type: ignore
from cc1101.config import TXConfig, Modulation # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore

import math
import subprocess
import time
from datetime import datetime
import struct
import sqlite3

import smbus # type: ignore

rfm9x = adafruit_rfm9x.RFM9x(busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO), DigitalInOut(board.CE1), DigitalInOut(board.D25), 433.0, high_power = True)
rfm9x.tx_power = 23

bus = smbus.SMBus(1)

On_GPS_time = False
send_cooldown = 4 # With data pulling 4x a second, sending rf 1x a second

# Connect to the car's database
con = sqlite3.connect('./CarTelemetry.sqlite')
cur = con.cursor()

# Create the initial table (Named main)
cur.execute('''
CREATE TABLE IF NOT EXISTS main (
    time REAL UNIQUE PRIMARY KEY,
    amp_hours REAL,
    voltage REAL,
    current REAL,
    speed REAL,
    miles REAL,
    throttle REAL,
    brake REAL,
    motor_temp REAL,
    batt_1 REAL,
    batt_2 REAL,
    batt_3 REAL,
    batt_4 REAL,
    GPS_x REAL,
    GPS_y REAL,
    laps NUMERIC
)
''')
con.commit()

# Find a list of days that are present in the database
cur.execute("""
    SELECT DISTINCT
        DATE(time, 'unixepoch') AS day
        FROM main
        ORDER BY day;
""")
days = cur.fetchall()

# Create individual views for each existing day if they do not exist
for day in days:
    cur.execute(f"""
    CREATE VIEW IF NOT EXISTS {day}
    AS SELECT * FROM main
    WHERE DATE(time, 'unixepoch') = '{day}';
    """)
con.commit()

# tx_config = TXConfig.new(
#     frequency=915,
#     modulation=Modulation.MSK, # Read up: https://en.wikipedia.org/wiki/Minimum-shift_keying
#     baud_rate=12, # Baud rate in kbps (Currently 3kb for each quarter second packet)
#     sync_word=0xD391, # Unique 16-bit sync word (Happens to be unicode for 펑 :) )
#     preamble_length=4, # Recommended: https://e2e.ti.com/support/wireless-connectivity/sub-1-ghz-group/sub-1-ghz/f/sub-1-ghz-forum/1027627/cc1101-preamble-sync-word-quality
#     packet_length=120, # In Bytes (Number of columns * 8)
#     tx_power=0.1, # dBm (Currently the max, expected to use 34.2 mA)
#     crc = True, # Enable a checksum
# )
# radio = CC1101("/dev/cc1101.0.0") # The default device path

# Setup Thermistor Values
R1 = 13000.0
logR2 = R2 = T = 0.0  # Initializing logR2, R2, and T as float values (defaulting to 0.0)
c1 = 1.009249522e-03
c2 = 2.378405444e-04
c3 = 2.019202697e-07

# Setup Send LED
sendLED = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(sendLED, GPIO.OUT)
GPIO.output(sendLED, 0)

# Setup i2C & Devices
i2c = busio.I2C(board.SCL, board.SDA)
analogA = ADS.ADS1115(i2c, address = 0x4B)
analogB = ADS.ADS1115(i2c, address = 0x4A)
CA704_ADDR = 0x28  # Replace with the actual I2C address -- Cycle Analyst
GPS704_ADDR = 0x29  # Replace with the actual I2C address -- GPS

# FOR SETTING UP 704', FOLLOW THIS GPT PAGE:
# https://chatgpt.com/share/673cbcb7-9a74-8010-9a24-c0a5603eb385

# Setup Analog In Ports
A0 = AnalogIn(analogA, ADS.P0) # battTemp1
A1 = AnalogIn(analogA, ADS.P1) # battTemp2
A2 = AnalogIn(analogA, ADS.P2) # battTemp3
A3 = AnalogIn(analogA, ADS.P3) # battTemp4
B0 = AnalogIn(analogB, ADS.P0) # motorTemp
B1 = AnalogIn(analogB, ADS.P1) # throttle
#B2 = AnalogIn(analogB, ADS.P2) # Port not used
B3 = AnalogIn(analogB, ADS.P3) # brake

# Setup UART for Cycle Anyalist
cycleAnalyst = serial.Serial('/dev/serial0',baudrate=9600,timeout=5)


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
        # data = read_from_uart(CA704_ADDR, 10)  # Adjust length for Cycle Analyst

        if cycleAnalyst.in_waiting > 0:
            line = cycleAnalyst.readline().decode('utf-8').strip()
            if line:
                amp_hours, voltage, current, speed, miles = line.split('\t')
                amp_hours = float(amp_hours)
                voltage = float(voltage)
                current = float(current)
                speed = float(speed)
                miles = float(miles)

                return amp_hours, voltage, current, speed, miles
        else:

            return float('nan'), float('nan'), float('nan'), float('nan'), float('nan')
    except Exception as e:
        print(f"Error in UART_CA function: {e}")
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan')


def set_system_time(timestamp, date):
    """Set the system time using the date command."""

    # Extract hours, minutes, and seconds from timestamp
    hours = timestamp[:2]
    minutes = timestamp[2:4]
    seconds = timestamp[4:]

    # Adjust for our timezone
    hours = int(hours)  - 4

    # Extract day, month, and year from date
    day = date[:2]
    month = date[2:4]
    year = 2000 + int(date[4:]) # Change this in 75 years; This is a limitation of the $GPRMC format

    # Format the date and time for the `date` command
    formatted_time = f"{year}-{month}-{day} {hours}:{minutes}:{seconds}"

    # Set the system time using the `date` command
    subprocess.run(["sudo", "date", "-s", formatted_time], check=True)
    print("System time sucessfully set to GPS time:", datetime.now())

    global On_GPS_time
    On_GPS_time = True

def read_full_sentence():
    sentence = ""
    for _ in range(10):
        try:
            data = bus.read_i2c_block_data(0x42, 0, 32)
            valid_data = ''.join([chr(i) for i in data if 32 <= i <= 126 or i in (10, 13)])
            sentence += valid_data
            if '\n' in valid_data:
                break
        except OSError as e:
            if e.errno == 5:
                print("ESP not online")
            else:
                print("Error:", e)
            break
        time.sleep(0.01)
    return sentence

# UART handler for GPS
def UART_GPS():
    try:
        data = read_full_sentence()
        # data = read_from_uart(GPS704_ADDR, 128)  # GPS data length can be longer (up to 255 bytes)

        if data:

            killall, gpstime, pos_status, lat, lat_dir, lon, lon_dir, speed, track_true, date, \
                mag_var, var_dir, checksum = data.split(',')

            # If no GPS fix, return nan for all variables
            if pos_status == 'V':
                print("No GPS fix!!!")
                return float('nan'), float('nan')

            # Set System time to gps time if not done yet
            if not On_GPS_time:
                set_system_time(gpstime, date)

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

            # Success!
            return GPS_x, GPS_y

    except Exception as e:
        print(f"Error in UART_GPS function: {e}")

    # didn't work out
    return float('nan'), float('nan')

def thermistor(idx):
    idx = idx*1024/32768
    R2 = R1 * (1023.0 / float(idx) - 1.0)
    logR2 = math.log(R2)
    T = 1.0 / (c1 + c2 * logR2 + c3 * logR2**3)
    T = T - 273.15  # Convert from Kelvin to Celsius
    #T = (T * 9.0) / 5.0 + 32.0  # Convert from Celsius to Fahrenheit
    return T

def mapTo(x, minI, maxI, minO, maxO):
    return (x-minI)/(maxI-minI)*(maxO-minO)+minO

def analogPull():
    # Throttle Value
    try:
        throttle = mapTo(B1.value, 6500, 33000, 0, 1000)
    except:
        throttle = float('nan')

    # Brake Value
    try:
        brake = mapTo(B3.value, 15000, 21500, 0, 1000)
    except:
        brake = float('nan')

    # Motor Temperature
    try:
        motor_temp = thermistor(B0.value)
    except:
        motor_temp = float('nan')

    # Battery 1 Temperature
    try:
        batt_1 = thermistor(A0.value)
    except:
        batt_1 = float('nan')

    # Battery 2 Temperature
    try:
        batt_2 = thermistor(A1.value)
    except:
        batt_2 = float('nan')

    # Battery 3 Temperature
    try:
        batt_3 = thermistor(A2.value)
    except:
        batt_3 = float('nan')

    # Battery 4 Temperature
    try:
        batt_4 = thermistor(A3.value)
    except:
        batt_4 = float('nan')

    return throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4

insert_data_sql = """
    INSERT INTO main (
        time, Throttle, Brake, Motor_temp, Batt_1, Batt_2, Batt_3, Batt_4,
        amp_hours, Voltage, Current, Speed, Miles, GPS_X, GPS_Y
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

while True:
    data_2_send = b''
    send_cooldown -= 1

    # Get Data
    timestamp = time.time()
    amp_hours, voltage, current, speed, miles = UART_CA()
    throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4 = analogPull()
    GPS_x, GPS_y = UART_GPS()

    data = [
        timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4, \
        amp_hours, voltage, current, speed, miles, GPS_x, GPS_y
    ]
    print(data)

    # Add data to the database:
    cur.execute(insert_data_sql, data)
    con.commit()
    print("Logged Data")

    # Attempt to send data
    if send_cooldown == 0:
        try:
            # Shift epoch to Jan 1 2025 to avoid excessive rounding
            data[0] -= time.mktime(datetime(2025, 1, 1, 0, 0, 0).timetuple())

            # Encode data as a 32 bit float
            packed_data = struct.pack('<' + 'f' * len(data), *data)

            # Send Data
            GPIO.output(sendLED, 1)
            rfm9x.send(packed_data)
            # radio.transmit(tx_config, data_2_send)
            print("Packet sent")
            GPIO.output(sendLED, 0)

            send_cooldown = 2

        except Exception as e:
            print("Error sending data:", e)
    
    time.sleep(0.25)

