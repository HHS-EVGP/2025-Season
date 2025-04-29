import sqlite3
from datetime import datetime
import struct

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
sock, _ = server.accept()
print("Client connected.")

# Initialize the socket data
values = [None] * 15 # * Data columns

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
#     tx_power=0.1, # dBm
#     crc=True, # Enable a checksum
# )
# radio = CC1101("/dev/cc1101.0.0", rx_config, blocking=True) # blocking=True means program will wait for a packet to be received

# Link the database to the python cursor
con = sqlite3.connect("EVGPTelemetry.sqlite")
cur = con.cursor()

# If main table does not exist as a table, create it
create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS main (
    time REAL UNIQUE PRIMARY KEY,
    Throttle REAL,
    Brake_Pedal REAL,
    Motor_temp REAL,
    Battery_1 REAL,
    Battery_2 REAL,
    Battery_3 REAL,
    Battery_4 REAL,
    ca_AmpHrs REAL,
    ca_Voltage REAL,
    ca_Current REAL,
    ca_Speed REAL,
    ca_Miles REAL,
    GPS_X REAL,
    GPS_Y REAL,
    laps NUMERIC
)"""

cur.execute(create_table_sql)
con.commit()

# Create individual views for each existing day if they do not exist
create_view_sql = """SELECT 
    'CREATE VIEW IF NOT EXISTS ' || day || ' AS SELECT * FROM main WHERE strftime(''%Y_%m_%d'', datetime(time, ''unixepoch'')) = ''' || day || ''';'
        FROM (
            SELECT DISTINCT strftime('%Y_%m_%d', datetime(time, 'unixepoch')) AS day
            FROM main
        )
        WHERE day NOT IN (
            SELECT name FROM sqlite_master WHERE type='view'
        );
        """
cur.execute(create_view_sql)
con.commit()

insert_data_sql = f"""
    INSERT INTO main (
        time, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
        ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles, GPS_X, GPS_Y
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

while True:
    
    # IN_data = []

    # Receive the next packets
    # packets = radio.receive() # Packets are only received if they pass the checksum
    #TODO Radio Recive! 
    packet = None
    packet = rfm9x.receive()

    print("Check for Packet")


    if not packet:
        time.sleep(0.4)
        print("No Packet")
        continue

    print("Yes Packet")
    # Extract the data from the packets
    # for packet in packets:
    #     for i in range(0, len(packet), 8):
    #         chunk = packet[i:i+8]
    #         IN_data.append(struct.unpack('<d', chunk)[0])

    if len(packet) % 8 != 0:
        print(f"Invalid packet size: {len(packet)} bytes, cannot unpack")
        continue  # Skip this iteration and wait for the next packet

    # Unpack the data only if the packet size is valid
    num_floats = len(packet) // 8  # Number of doubles (each double is 8 bytes)
    floats = struct.unpack('<' + 'd' * num_floats, packet)

    print(floats)
    # Assign the extracted data to the respective variables
    try:
        timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4, \
            amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = floats
    except Exception as e:
        print(f"Error: {e}")
        continue

    # timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4, \
    #     amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = IN_data

    # Interpret nan as NULL in the database
    for var in [throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4,
                amp_hours, voltage, current, speed, miles, GPS_x, GPS_y]:
        if var == float('nan'):
            var = None

    # Insert the data into the database
    values = [
         timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4,
         amp_hours, voltage, current, speed, miles, GPS_x, GPS_y
    ]
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
