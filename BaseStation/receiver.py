import sqlite3
from datetime import datetime, timedelta
import time
import struct
import math

import socket
import pickle
import os

import cc1101

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

## Create individual views for each existing day if they do not exist
for day in days:
    cur.execute(f"""
    CREATE VIEW IF NOT EXISTS '{day[0]}'
    AS SELECT * FROM main
    WHERE DATE(time, 'unixepoch') = '{day[0]}';
    """)
con.commit()

insert_data_sql = f"""
    INSERT INTO main (
        time, throttle, brake, Motor_temp, batt_1, batt_2, batt_3, batt_4,
        amp_hours, voltage, current, speed, miles, GPS_X, GPS_Y
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
with cc1101.CC1101(spi_bus=0, spi_chip_select=0) as radio:
    ## Transmission Variables ##
    radio._enable_receive_mode()
    #radio.set_sync_mode(0b10, False) # No carrier sense threshold
    #radio._set_filter_bandwidth(60)

    radio.set_base_frequency_hertz(433000000)
    radio._set_modulation_format(cc1101.ModulationFormat.MSK)
    radio.set_symbol_rate_baud(5000)
    radio.set_sync_word(b'\x91\xd3')
    radio.set_preamble_length_bytes(4)

    print("Radio config:", radio)
    waitnum = 0

    # Lenths of seperate encoding types (See collector.py, line 345)
    len64 = 8
    len16 = 14
    len32 = 28

    expected_len = len64 + len16 + len32

    while True:
        # Receive a packet
        # GIPO 24 goes High when a packet is avalable
        indump = radio._wait_for_packet(timedelta(seconds=5), gdo0_gpio_line_name=b"GPIO24")

        if indump == None:
            print(f"Waited for packet {waitnum} time(s)")
            waitnum += 1
            continue

        packet = indump.payload()

        if indump.checksum_valid == False:
            print("CRC Failed!!!")
            #continue

        if len(packet) != expected_len:
            print(f"Invalid packet size: {len(packet)} bytes!")

        try:
            # Unpack the 64 bit section
            in64 = struct.unpack("<" + "d" *len64, packet[:len64])
            timestamp = in64[0]

            # Unpack the 16 bit section
            in16 = struct.unpack("<" + "e", *len16, packet[len64:(len64+len16)])
            throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4 = in16

            # Unpackt the 32 bit section
            in32 = struct.unpack("<" + "f" * len32, packet[len64+len16:])
            amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = in32

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
