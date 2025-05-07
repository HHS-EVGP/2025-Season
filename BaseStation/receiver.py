import sqlite3
from datetime import datetime
import struct
import math

import socket
import pickle
import os

import busio # type: ignore
import time
import board # type: ignore

import adafruit_rfm9x # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore
rfm9x = adafruit_rfm9x.RFM9x(busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO), DigitalInOut(board.CE1), DigitalInOut(board.D25), 433.0, high_power = True)
rfm9x.tx_power = 23

# from cc1101 import CC1101 # type: ignore
# from cc1101.config import RXConfig, Modulation # type: ignore

prev_values = [None] * 15

SOCKETPATH = "/tmp/telemSocket"

# Remove existing socket file if it exists
if os.path.exists(SOCKETPATH):
    os.remove(SOCKETPATH)

# Create a Unix socket and listen
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKETPATH)
server.listen(1)

print("Server is waiting for connection...")
sock, _ = server.accept() # Is blocking untill client connected
print("Client connected.")

# Initialize the socket data
values = [None] * 15 # Number of Data columns

# Initial data send
data = pickle.dumps(values)
sock.sendall(data)

## Transmission variables ##
# rx_config = RXConfig.new(
#     frequency=915,
#     modulation=Modulation.MSK, # Read up: https://en.wikipedia.org/wiki/Minimum-shift_keying
#     baud_rate=12, # Baud rate in kbps (Currently 3kb for each quarter second packet)
#     sync_word=0xD391, # Unique 16-bit sync word (Happens to be unicode for 펑 :) )
#     preamble_length=4, # Recommended: https://e2e.ti.com/support/wireless-connectivity/sub-1-ghz-group/sub-1-ghz/f/sub-1-ghz-forum/1027627/cc1101-preamble-sync-word-quality
#     packet_length=120, # In Bytes (Number of columns * 8)
#     bandwidth=58,
#     carrier_sense=+6
#     crc=True, # Enable a checksum
# )
# radio = CC1101("/dev/cc1101.0.0", rx_config, blocking=True) # blocking=True means program will wait for a packet to be received

# Link the database to the python cursor
con = sqlite3.connect("EVGPTelemetry.sqlite")
cur = con.cursor()

# If main table does not exist as a table, create it
cur.execute("""
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
""")
con.commit()

# Find a list of days that are present in the database
cur.execute('''
    SELECT DISTINCT
        DATE(time, 'unixepoch') AS day
        FROM main
        ORDER BY day;
''')
days = cur.fetchall()

# Create individual views for each existing day if they do not exist
for day in days:
    cur.execute(f"""
    CREATE VIEW IF NOT EXISTS {day}
    AS SELECT * FROM main
    WHERE DATE(time, 'unixepoch') = '{day}';
    """)
con.commit()

insert_data_sql = f"""
    INSERT INTO main (
        time, throttle, brake, Motor_temp, batt_1, batt_2, batt_3, batt_4,
        amp_hours, voltage, current, speed, miles, GPS_X, GPS_Y
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

while True:
    # Receive the next packets
    # packets = radio.receive() # Is blocking and buffering

    packet = None
    packet = rfm9x.receive()

    print("Check for Packet")
    if not packet:
        time.sleep(0.4)
        print("No Packet")
        continue

    print("Received Packet")

    if len(packet) % 4 != 0:
        print(f"Invalid packet size: {len(packet)} bytes, cannot unpack")
        continue  # Skip this iteration and wait for the next packet

    try:
        # Unpack the data
        num_floats = len(packet) // 4  # Number of floats (each double is 4 bytes)
        floats = struct.unpack('<' + 'f' *num_floats, packet)
        print(floats)

        # Assign the extracted data to the respective variables
        timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4, \
            amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = floats
        
        # Shift the epoch back to Jan 1 1970 for storage
        floats[0] += time.mktime(datetime(2025, 1, 1, 0, 0, 0).timetuple())

    except Exception as e:
        print(f"Error extracting data: {e}")
        continue

    values = [
         timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4,
         amp_hours, voltage, current, speed, miles, GPS_x, GPS_y
    ]

    # If a value is nan, replace it with None
    values = [None if math.isnan(x) else x for x in values]

    # Insert the data into the database
    cur.execute(insert_data_sql, values)
    con.commit()

    # If a variable in values is None, replace it with what it was last
    for i in range(len(values)):
        if values[i] is None:
            values[i] = prev_values[i]

    # Pickle the socket data and send it
    data = pickle.dumps(values)
    sock.sendall(data)

    prev_values = values
