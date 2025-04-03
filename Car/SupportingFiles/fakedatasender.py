import struct
import time
from datetime import datetime
import subprocess
import random
import sqlite3

freq = 915 # Frequency in MHz
Pus = 10 # Duration of a 1 or 0 pulse in µs
Gus = 0 # Duration of gap between bits in µs
preamble = "1" * 128 

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
    for var in [timestamp, amp_hours, voltage, current, speed, miles, throttle, brake, motor_temp, batt_1, batt_2, batt_3, batt_4, GPS_x, GPS_y, GPS_z]:
        bit_string = ''.join(f'{byte:08b}' for byte in struct.pack('>d', var))
        data_2_send += bit_string

    # Send data
    subprocess.run(["sudo ./sendook -0", Pus, "-1", Pus, "-g", Gus, "-f", freq, preamble, data_2_send]) # Uses GPIO 4 (Pin 7)
    print("Sent:", data_2_send,)

    # Insert data into the database
    insert_data_sql = """
        INSERT INTO {} (
            time, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
            ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles, GPS_X, GPS_Y, GPS_Z,
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """.format(table_name)

    cur.execute(insert_data_sql, (
        timestamp, throttle, brake, motor_temp, batt_1, batt_2, batt_3,
        batt_4, amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z
    ))
    con.commit()

    time.sleep(1)