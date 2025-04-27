import sqlite3
from datetime import datetime
import struct

import socket
import pickle
import os

from cc1101 import CC1101 # type: ignore
from cc1101.config import RXConfig, Modulation # type: ignore

SOCKETPATH = "/tmp/telemSocket"

# Remove existing socket file if it exists
if os.path.exists(SOCKETPATH):
    os.remove(SOCKETPATH)

# Create a Unix socket and listen
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKETPATH)
server.listen(1)

print("Server is waiting for connection...")
conn, _ = server.accept()
print("Client connected.")

# Initialize the socket data
socketData = [None] * 15 # * Data columns

# Initial data send
data = pickle.dumps(socketData)
conn.sendall(data)

# Transmission variables ##
rx_config = RXConfig.new(
    frequency=915,
    modulation=Modulation.MSK, # Read up: https://en.wikipedia.org/wiki/Minimum-shift_keying
    baud_rate=12, # Baud rate in kbps (Currently 3kb for each quarter second packet)
    sync_word=0xD391, # Unique 16-bit sync word (Happens to be unicode for 펑 :) )
    preamble_length=4, # Recommended: https://e2e.ti.com/support/wireless-connectivity/sub-1-ghz-group/sub-1-ghz/f/sub-1-ghz-forum/1027627/cc1101-preamble-sync-word-quality
    packet_length=120, # In Bytes (Number of columns * 8)
    tx_power=0.1, # dBm
    crc=True, # Enable a checksum
)
radio = CC1101("/dev/cc1101.0.0", rx_config, blocking=True) # blocking=True means program will wait for a packet to be received

# Link the database to the python cursor
con = sqlite3.connect("BaseStation/EVGPTelemetry.sqlite")
cur = con.cursor()

# Define the name of today's table
table_name = "hhs_" + datetime.now().strftime("%Y_%m_%d")
print("Today's table name is:", table_name)

# If table_name does not exist as a table, create it
create_table_sql = """
    CREATE TABLE IF NOT EXISTS {} (
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
)""".format(table_name)

cur.execute(create_table_sql)
con.commit()

while True:
    IN_data = []

    # Receive the next packets
    packets = radio.receive() # Packets are only received if they pass the checksum

    # Extract the data from the packets
    for packet in packets:
        for i in range(0, len(packet), 8):
            chunk = packet[i:i+8]
            IN_data.append(struct.unpack('<d', chunk)[0])

    # Assign the extracted data to the respective variables
    timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4, \
    amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = IN_data

    # Interpret nan as NULL
    for var in [throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4,
                amp_hours, voltage, current, speed, miles, GPS_x, GPS_y]:
        if var == float('nan'):
            var = None

    # Insert the data into the database
    insert_data_sql = """
        INSERT INTO {} (
            time, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
            ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles, GPS_X, GPS_Y
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    cur.execute(insert_data_sql, (
        timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3,
        batt_4, amp_hours, voltage, current, speed, miles, GPS_x, GPS_y
    ))
    con.commit()

    # Update the socket data and send it
    socketData = [
         timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4, \
         amp_hours, voltage, current, speed, miles, GPS_x, GPS_y
    ]

    data = pickle.dumps(socketData)
    conn.sendall(data)
