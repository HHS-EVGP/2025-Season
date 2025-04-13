import struct
import time
from datetime import datetime
import random
import sqlite3

freq = 915 # Frequency in MHz
from cc1101 import CC1101 # type: ignore
from cc1101.config import TXConfig, Modulation # type: ignore

# Transmission Variables
freq = 915 # Frequency in MHz

tx_config = TXConfig.new(
    frequency=freq,
    modulation=Modulation.MSK, # Read up: https://en.wikipedia.org/wiki/Minimum-shift_keying
    baud_rate=12.0, # Baud rate in kbps (Currently 3kb for each quarter second packet)
    sync_word=0xD391, # Unique 16-bit sync word (Happens to be unicode for 펑 :) )
    preamble_length=4, # Recommended: https://e2e.ti.com/support/wireless-connectivity/sub-1-ghz-group/sub-1-ghz/f/sub-1-ghz-forum/1027627/cc1101-preamble-sync-word-quality
    packet_length=104, # In Bytes (Number of columns * 8)
    tx_power=0.1, # dBm (see: https://www.ti.com/lit/an/swra151a/swra151a.pdf)
)
radio = CC1101("/dev/cc1101.0.0") # The default device path

# Set Up a database to compare to the received database
con = sqlite3.connect("./fakedatalog.sqlite")
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
    GPS_Z REAL
)""".format(table_name)

cur.execute(create_table_sql)
con.commit()

while True:
    data_2_send = b''

    # Generate fake data
    timestamp = time.time()
    amp_hours = random.uniform(-300, 300)
    voltage = random.uniform(-300, 300)
    current = random.uniform(-300, 300)
    speed = random.uniform(-300, 300)
    miles = random.uniform(-300, 300)
    throttle = random.uniform(-300, 300)
    brake = random.uniform(-300, 300)
    motor_temp = random.uniform(-300, 300)
    batt_1 = random.uniform(-300, 300)
    batt_2 = random.uniform(-300, 300)
    batt_3 = random.uniform(-300, 300)
    batt_4 = random.uniform(-300, 300)
    GPS_x = random.uniform(-300, 300)
    GPS_y = random.uniform(-300, 300)
    GPS_z = random.uniform(-300, 300)

    # Encode data
    for var in timestamp, amp_hours, voltage, current, speed, miles, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4:
        data_2_send + struct.pack('<d', var)

    radio.transmit(tx_config, data_2_send)
    print("Packet sent")
        
    # Insert data into the database
    insert_data_sql = """
        INSERT INTO {} (
            time, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
            ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles, GPS_X, GPS_Y, GPS_Z
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """.format(table_name)

    cur.execute(insert_data_sql, (
        timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3,
        batt_4, amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z
    ))
    con.commit()

    time.sleep(0.25)