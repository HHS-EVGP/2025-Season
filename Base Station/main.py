import adafruit_rfm9x
import board
import busio
import csv
import os
import time
from datetime import datetime
from digitalio import DigitalInOut

# Initialize the RFM9x LoRa Radio with specified SPI and GPIO configurations
rfm9x = adafruit_rfm9x.RFM9x(
    busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO),
    DigitalInOut(board.CE1),
    DigitalInOut(board.D25),
    433.0,
    high_power=True
)
rfm9x.tx_power = 23  # Set transmission power level

index = 1  # Start with the first index for the data log file
counter_var = 0  # Initialize a counter to keep track of data entries

# Find the next available log file name in the specified directory
while os.path.exists(f"/home/data/front_end/{index:03}.data.log"):
    index += 1
new_file_name = f"/home/data/front_end/{index:03}.data.log"

# Define the CSV column headers
fieldnames = [
    'time', 'counter',
    'throttle', 'Brake_Pedal',
    'motor_temp', 'Battery_1', 'Battery_2', 'Battery_3', 'Battery_4',
    'ca_AmpHrs', 'ca_Voltage', 'ca_Current', 'ca_Speed', 'ca_Miles'
]

# Set the expected school identifier for filtering incoming data
school_id = 'hhs'

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
    with open(new_file_name, 'x', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if counter_var == 0:
            writer.writeheader()  # Write CSV headers only once

        counter_var += 1  # Increment the data entry counter
        packet = None

        # Attempt to receive a packet from the LoRa radio
        packet = rfm9x.receive()

        # If no packet is received, log the time and counter
        if packet is None:
            print('- Waiting for PKT -')
            writer.writerow({'time': datetime.now(), 'counter': counter_var})
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
                    # Write the processed data to the CSV file
                    writer.writerow({
                        'time': datetime.now(), 'counter': counter_var,
                        'throttle': throttle, 'Brake_Pedal': brake_pedal,
                        'motor_temp': motor_temp, 'Battery_1': Battery_temp_1,
                        'Battery_2': Battery_temp_2, 'Battery_3': Battery_temp_3,
                        'Battery_4': Battery_temp_4, 'ca_AmpHrs': amp_hours, 'ca_Voltage': voltage,
                        'ca_Current': current, 'ca_Speed': speed, 'ca_Miles': miles
                    })
                except Exception as err:
                    printError(err)
            except Exception as err:
                printError(err)
        csv_file.close()
