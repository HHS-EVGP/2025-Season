import numpy as np
from gnuradio import gr

import sqlite3
from datetime import datetime
import struct

# Transmission variables
preamble = np.ones(128, dtype=np.float32) # Array Equivilant of "1" * 128
packet_length = 1024 # Packet length in bits (Determined by columns of data * 64)
lastPkt = None
firstHalf = None
packet = None

# Link the database to the python cursor
con = sqlite3.connect("./EVGPTelemetry.sqlite")
cur = con.cursor()

# Define the name of today's table
table_name = "hhs_" + datetime.now().strftime("%Y_%m_%d")
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
    ca_Miles REAL,
    GPS_X REAL,
    GPS_Y REAL,
    GPS_Z REAL
)""".format(table_name)

cur.execute(create_table_sql)
con.commit()

# Initialize variables to store data
timestamp = None
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
GPS_x = None
GPS_y = None
GPS_z = None

class blk(gr.sync_block):
    """Take the raw thresholded input data, decode it, and store it in an sqlite database."""

    def __init__(self):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Decode OOK and Log in DB',
            in_sig=[np.float32], # float32 is the best gnuradio will give us
            out_sig= None
        )

    def work(self, input_items):
        input_chunk = input_items[0] # the lenth of input_chunk is whatever gnuradio decides is the optimal buffer
        input_dump = np.append(input_chunk)

        # TODO: Refine logic: if not preamble, add input chunk, etc.
        # Scan the input_dump for the pramble
        for i in range(len(input_dump) - len(preamble)):
            window = input_dump[i:i + len(preamble)]
            if np.array_equal(window, preamble):

                # If half of a packet is logged, finish it
                if firstHalf != None:
                    packet = np.concatenate((firstHalf, input_dump[:packet_length - len(firstHalf)]))
                    firstHalf = None

                # If the packet is incomplete, log the first section and exit
                elif len(input_dump)/8 - i < packet_length:
                    firstHalf = input_dump[i + len(preamble):]
                    return len(input_chunk) # Exit
                
                # If the packet is complete, log it
                else:
                    packet = input_dump[i + len(preamble) :i + len(preamble) + packet_length]
            
            #Ensure that the packet will be split between at most two input_dumps
            elif len(input_dump) < packet_length + len(preamble):
                input_dump = np.append(input_chunk)
                return len(input_chunk) # Exit
            
            else:
                print("Waiting for Packet...")
                packet = None

        # Trim down input_dump if needed
        if len(input_dump) > packet_length + len(preamble):
            input_dump = input_dump[input_dump - (packet_length+len(preamble)):]

        # Extract the rest of the data
        if packet != None:
            IN_data = []
            for j in range(len(packet), 64):
                byte_chunk = packet[j:j + 64]
                # Convert 8 bits (1s and 0s) from the array into a single byte
                current_byte = ''.join(map(str, byte_chunk[:8*t].astype(float)))

                float_value = struct.unpack('!f', int_value.to_bytes(8, byteorder='big'))[0]
                IN_data.append(float_value)

            # Assign the extracted data to the respective variables
            timestamp, throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2, Battery_temp_3, Battery_temp_4, \
            amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z = IN_data

            # Interpret -inf as NULL
            for var in [throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2, Battery_temp_3, Battery_temp_4,
                        amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z]:
                if var == float('-inf'):
                    var = None
            
            # Insert the data into the database
            insert_data_sql = """
                INSERT INTO {} (
                    time, Throttle, Brake_Pedal, Motor_temp, Battery_1, Battery_2, Battery_3, Battery_4,
                    ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles, GPS_X, GPS_Y, GPS_Z,
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.format(table_name)
            
            cur.execute(insert_data_sql, (
                timestamp, throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2, Battery_temp_3,
                Battery_temp_4, amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z
            ))
            con.commit()

        return len(input_chunk) # Exit