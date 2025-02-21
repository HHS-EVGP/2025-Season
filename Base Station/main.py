import adafruit_rfm9x # type: ignore
import board # type: ignore
import busio # type: ignore
import time
from datetime import datetime
from digitalio import DigitalInOut # type: ignore
import sqlite3

freq = 915.0 #For ISM Reigion 2

# Initialize the RFM9x LoRa Radio with specified SPI and GPIO configurations
rfm9x = adafruit_rfm9x.RFM9x(
    busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO),
    DigitalInOut(board.CE1),
    DigitalInOut(board.D25),
    freq,
    high_power=True
)
rfm9x.tx_power = 12  # Set transmission power level

# Set the expected school identifier for filtering incoming data
school_id = 'hhs'

# Initialize a counter to keep track of data entries
counter_var = 0

#Link the database to the python cursor
con = sqlite3.connect("EVGPTelemetry.sqlite")
cur = con.cursor()

# Define the name of today's table
table_name = school_id + "_" + datetime.now().strftime("%Y-%m-%d")
print("Today's table name is:", table_name,)

# If table_name does not exist as a table, create it
# According to GitHub copilot, this method is safer
create_table_sql = """
CREATE TABLE IF NOT EXISTS {} (
    time NUMERIC UNIQUE PRIMARY KEY,
    counter INTEGER,
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

def printError(error):
    """Prints formatted error messages to the console."""
    print("_" * 20)
    print(" " * 7, "ERROR!", " " * 7)
    print("\/" * 10)
    print(" ")
    print(error)
    print(" ")
    print("_" * 20)

while True:
    time.sleep(0.15)  # Pause for a short duration between data checks

    # Increment the data entry counter
    counter_var += 1

    # Attempt to receive a packet from the LoRa radio
    packet = None
    packet = rfm9x.receive()

    # If no packet is received, notify user
    if packet is None:
        print('- Waiting for PKT -')
    else:
        print(packet)

        try:
            # Convert the received packet from bytes to a UTF-8 string
            current_packet = str(packet, "utf-8")

            try:
                # Split the packet into different data sections
                all_data = current_packet.split('|')

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

            except Exception as err:
                printError(err)

            try:
                # Write the processed data to the correct DB table
                #The ?s in the SQL statment are defined in the cur.execute() function. Doing it this way is more protected aganst SQL injection, wich is good form.
                insert_data_sql = """
                INSERT INTO {} (
                    time, counter, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
                    ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.format(table_name)

                cur.execute(insert_data_sql, (
                    datetime.now().strftime("%H:%M:%S.%f"), counter_var, throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2,
                    Battery_temp_3, Battery_temp_4, amp_hours, voltage, current, speed, miles
                ))
                con.commit()

            except Exception as err:
                    printError(err)

        except Exception as err:
            printError(err)
