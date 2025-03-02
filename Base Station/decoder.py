import sqlite3
from datetime import datetime
import time
import json

school_id = "hhs"

#Transmission Variables
freq = 915 # Frequency  in MHz
sendtimes = 1 # Number of times to send the message (For redundancy)

#Current values are as small as is possible
Zus = 12 # Pulse duration of bit 0 in µs
Ous = 13 # Pulse duration of bit 1 in µs
Gus = 11 # Duration of gap between bits in µs
Pus = 14 # Duration of pauses between messages in µs

#Link the database to the python cursor
con = sqlite3.connect("EVGPTelemetry.sqlite")
cur = con.cursor()

# Define the name of today's table
table_name = school_id + "_" + datetime.now().strftime("%Y_%m_%d")
print("Today's table name is:", table_name,)

# If table_name does not exist as a table, create it
create_table_sql = """
CREATE TABLE IF NOT EXISTS {} (
    time NUMERIC UNIQUE PRIMARY KEY,
    Throttle NUMERIC,
    Brake_Pedal NUMERIC,
    Motor_temp NUMERIC,
    Battery_1 NUMERIC,
    Battery_2 NUMERIC,
    Battery_3 NUMERIC,
    Battery_4 NUMERIC,
    ca_AmpHrs NUMERIC,
    ca_Voltage NUMERIC,
    ca_Current NUMERIC,
    ca_Speed NUMERIC,
    ca_Miles NUMERIC
)
""".format(table_name) #The contents of the .format are applied to the {} in the SQL statement

cur.execute(create_table_sql)
con.commit()

# Initialize variables to store sensor data
throttle = None
brake_pedal = None
motor_temp = None
Battery_temp_1 = None
Battery_temp_2 = None
Battery_temp_3 = None
Battery_temp_4 = None
amp_hours = None
voltage = None
current = None
speed = None
miles = None

while True:

    # Gnuradio spits out revieved_bytes

    received_string = ' '.join(received_bytes[i:i+8] for i in range(0, len(received_bytes), 8))

    if received_string == none:
        time.sleep(0.15)  # Pause for a short duration between data checks
        continue

        # Convert the received packet from bytes to a UTF-8 string

    current_row = chr(int("01111110", 2))

    # Split the packet into different data sections
    all_data = current_row.split('|')

    # Unpack data sections into individual variables
    school_ID, IN_throttle, IN_brake, IN_tempatureData, IN_cycle_analyst, IN_extra_NULL = map(str, all_data)

    # Process data only if the school ID matches the expected ID
    if school_ID == school_id:
        # Parse throttle data
        if IN_throttle.startswith("throttle,"):
            values = IN_throttle.split(',')
            throttle = values[1:][0] if values[1:][0] != "None" else ""
         # Parse brake pedal data
        if IN_brake.startswith("brake,"):
            values = IN_brake.split(',')
            brake_pedal = values[1:][0] if values[1:][0] != "None" else ""
         # Parse temperature data for the motor and batteries
        if IN_tempatureData.startswith("tempData,"):
            values = IN_tempatureData.split(',')
            motor_temp, Battery_temp_1, Battery_temp_2, Battery_temp_3, Battery_temp_4 = values[1:]
            motor_temp = motor_temp if motor_temp != "None" else ""
            Battery_temp_1 = Battery_temp_1 if Battery_temp_1 != "None" else ""
            Battery_temp_2 = Battery_temp_2 if Battery_temp_2 != "None" else ""
            Battery_temp_3 = Battery_temp_3 if Battery_temp_3 != "None" else ""
            Battery_temp_4 = Battery_temp_4 if Battery_temp_4 != "None" else ""
         # Parse cycle analyst data
        if IN_cycle_analyst.startswith("CA,"):
            values = IN_cycle_analyst.split(',')
            amp_hours, voltage, current, speed, miles = values[1:]
            amp_hours = amp_hours if amp_hours != "None" else ""
            voltage = voltage if voltage != "None" else ""
            current = current if current != "None" else ""
            speed = speed if speed != "None" else ""
            miles = miles if miles != "None" else ""

    # Write the processed data to the correct DB table
    insert_data_sql = """
    INSERT INTO {} (
        time, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
        ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """.format(table_name)

    cur.execute(insert_data_sql, (
        datetime.now().strftime("%H:%M:%S.%f"), throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2,
        Battery_temp_3, Battery_temp_4, amp_hours, voltage, current, speed, miles
    ))
    con.commit()

    #Write the last processed line data into a JSON file
    data = {
        "time": datetime.now().strftime("%H:%M:%S.%f"),
        "Throttle": throttle,
        "Brake_Pedal": brake_pedal,
        "Motor_temp": motor_temp,
        "Battery_1": Battery_temp_1,
        "Battery_2": Battery_temp_2,
        "Battery_3": Battery_temp_3,
        "Battery_4": Battery_temp_4,
        "ca_AmpHrs": amp_hours,
        "ca_Voltage": voltage,
        "ca_Current": current,
        "ca_Speed": speed,
        "ca_Miles": miles
    }

    with open("lastline.json", "w") as json_file:
        json.dump(data, json_file)
