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
#for day in days:
#    cur.execute(f"""
#    CREATE VIEW IF NOT EXISTS {day}
#    AS SELECT * FROM main
#    WHERE DATE(time, 'unixepoch') = '{day}';
#    """)
#con.commit()

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

    while True:
        lastHalf = None

        # Wait for a packet
        if radio._wait_for_packet(timedelta(seconds=5), gdo0_gpio_line_name=b"GPIO24") == None: # Timeout of 5 seconds
            print(f"Waiting for packet for the {waitnum}th time")
            waitnum += 1
            continue

        # Receive a packet
        indump = radio._get_received_packet()
        if indump is None:
            continue

        waitnum = 0
        packet = indump.payload
        print("Received Packet part")

        if len(packet) % 4 != 0:
            print(f"Invalid packet size: {len(packet)} bytes, cannot unpack")
            continue  # Skip this iteration and wait for the next packet

        print(packet)
        try:
            # Unpack the data
            num_floats = len(packet) // 4  # Number of floats (each double is 4 bytes)
            floats = struct.unpack('<' + 'f' *num_floats, packet)

            # If this is the second half, and we have the first half, join them
            if floats.pop() == 1:
                if lastHalf != None:
                    # Merge the two halves of the packet
                    floats = lastHalf + floats
                    print("Received full packet!")

                else:
                    print("Only have second half of packet. Dropping...")
                    continue

            # If this is a first half, remember it
            elif floats.pop == 0:
                lastHalf = floats
                continue

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
