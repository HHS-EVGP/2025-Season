import sqlite3
from datetime import datetime
import time
import json
import os

school_id = "hhs"

#Link the database to the python cursor
con = sqlite3.connect("EVGPTelemetry.sqlite")
cur = con.cursor()

# Define the name of today's table
table_name = school_id + "_" + datetime.now().strftime("%Y_%m_%d")
print("Today's table name is:", table_name,)

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
    ca_Miles REAL
)
""".format(table_name) #The contents of the .format are applied to the {} in the SQL statement

cur.execute(create_table_sql)
con.commit()

# Initialize variables to store sensor data
time = None
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

# Function to trim the sink file if needed
def trim_file(filepath, max_size):
    file_size = os.path.getsize(filepath)
    if file_size <= max_size:
        return
    
    excess_bytes = file_size - max_size
    
    with open(filepath, 'rb') as f:
        f.seek(excess_bytes)  # Skip the excess bytes
        data = f.read()
    
    with open(filepath, 'wb') as f:
        f.write(data)
    
    print(f"Trimmed {excess_bytes} bytes from the start of {filepath}.")


while True:

    # Gnuradio saves array of received bits into a file
    # Come back to this: https://wiki.gnuradio.org/index.php/File_Sink#Reading_from_Python

    received_bytes = ""

    received_string = ' '.join(received_bytes[i:i+8] for i in range(0, len(received_bytes), 8))

    if received_string == None:
        time.sleep(0.15)  # Pause for a short duration between data checks
        continue

        # Convert the received packet from bytes to a UTF-8 string

    current_row = chr(int("11111111", 2))

    # Split the packet into different data sections
    all_data = current_row.split('|')

    # Unpack data sections into individual variables
    school_ID, IN_time, IN_throttle, IN_brake, IN_tempatureData, IN_cycle_analyst, IN_extra_NULL = map(str, all_data)

    # Process data only if the school ID matches the expected ID
    if school_ID == school_id:
        # Parse Timestamp
        if IN_time.startswith("time,"):
            values = IN_time.split(',')
            timestamp = values[1:][0] if values[1:][0] != "None" else ""
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
        timestamp, throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2,
        Battery_temp_3, Battery_temp_4, amp_hours, voltage, current, speed, miles
    ))
    con.commit()

    #Write the last processed line data into a JSON file
    data = {
        "time": timestamp,
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

    # Trim the sink file if needed:
    trim_file("./receiver/rfsink", 5242880) # 5 MB
