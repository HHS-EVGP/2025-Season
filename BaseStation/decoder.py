import numpy as np
from gnuradio import gr

import sqlite3
from datetime import datetime
import struct

# Transmission variables
preamble = np.ones(128, dtype=np.float32) # Array Equivilant of "1" * 128
packet_length = 1024 # Packet length in bits (Determined by columns of data * 64)
packet = None

# Link the database to the python cursor
con = sqlite3.connect("./EVGPTelemetry.sqlite")
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


class blk(gr.sync_block):
    """Take the raw thresholded input data, decode it, and store it in an sqlite database."""

    def __init__(self):
        """Decode and store the data: https://github.com/HHS-EVGP/2025-Season"""
        gr.sync_block.__init__(
            self,
            name='Decode OOK and Log in DB',
            in_sig=[np.float32], # float32 is the best gnuradio will give us
            out_sig= None
        )

    def work(self, input_items):
        input_chunk = input_items[0] # the lenth of input_chunk is whatever gnuradio decides is the optimal buffer
        input_dump = np.append(input_chunk)

        # Scan the input_dump for the pramble
        for i in range(len(input_dump) - len(preamble)):
            window = input_dump[i:i + len(preamble)]
            if np.array_equal(window, preamble):
                #Trim to i
                input_dump = input_dump[i:]
                
                # If the packet is incomplete, exit to get more bits
                if len(input_dump) < len(preamble)+packet_length:
                    return len(input_chunk)

                # If the packet is complete, log it
                else:
                    # Trim down the input dump to i
                    
                    packet = input_dump[len(preamble) :len(preamble) + packet_length]                    
                    break

        # If no preamble found trim to i
        if preamble == None:
            input_dump = input_dump[i:]
                
        # Extract the data
        else:
            IN_data = []
            for j in range(0, len(packet), 64):
                in_bits = packet[j:j + 64]

                # convert from bits to bytes to float
                decoded_float = struct.unpack(">d", np.packbits(packet))[0]
                # decoded_float = struct.unpack('>d', int(in_bits, 2).to_bytes(8, 'big'))[0]
                IN_data.append(decoded_float)

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
                    ca_AmpHrs, ca_Voltage, ca_Current, ca_Speed, ca_Miles, GPS_X, GPS_Y, GPS_Z
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.format(table_name)

            cur.execute(insert_data_sql, (
                timestamp, throttle, brake_pedal, motor_temp, Battery_temp_1, Battery_temp_2, Battery_temp_3,
                Battery_temp_4, amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z
            ))
            con.commit()

            packet = None

        return len(input_chunk) # Exit