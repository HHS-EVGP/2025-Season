# SPDX-FileCopyrightText: 2018 Brent Rubell for Adafruit Industries
# SPDX-License-Identifier: MIT
# Wiring Check, Pi Radio w/RFM9x
# Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
# Author: Brent Rubell for Adafruit Industries

# Last updated on 1/23/2024 

import csv
import os
import time
from datetime import datetime

index = 1
conter = 0

# while os.path.exists(f"/home/data/front_end/{index}.data.csv"):
#     index += 1
new_file_name = f"/home/data/front_end/2.data.csv"

fieldnames = [
    'time','counter',
    'throttle','Brake_Pedal',
    'motor_temp','Battery_1','Battery_2','Battery_3','Battery_4',
    'ca_AmpHrs','ca_Voltage','ca_Current','ca_Speed','ca_Miles'
    ]

school_id = 'hhs'

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

def printError(erorr):
    print("_"*20)
    print(" "*7,"ERORR!"," "*7)
    print("\/"*10)
    print(" ")
    print(erorr)
    print(" ")
    print("_"*20)
    
while True:
    time.sleep(0.15)
    
    conter += 1
    packet = "hhs|throttle,3|brake,56|tempData,9,None,None,None,None|CA,None,None,None,None,None|"

    # check for packet rx

    # Packet should look like this: 
    # hhs|throttle,None|brake,None|tempData,None,None,None,None,None|CA,None,None,None,None,None|
    

    current_packet = packet

    all_data = current_packet.split('|')
    
    school_ID, IN_throttle, IN_brake, IN_tempatureData, IN_cycle_analyst, IN_extra_NULL = map(str, all_data)
    
    if school_ID == school_id:

        if IN_throttle.startswith("throttle,"):
            values = IN_throttle.split(',')
            print(f"values[1:] :: {values[1:]}")
            print(f"values[1:][0] :: {values[1:][0]}")
            throttle = values[1:][0] # The [0] MAY cause issues... I do not know yet.
            if throttle == "None":
                throttle = ""

        if IN_brake.startswith("brake,"):
            values = IN_brake.split(',')
            brake_pedal = values[1:][0] # The [0] MAY cause issues... I do not know yet.
            if brake_pedal == "None":
                brake_pedal = ""

        if IN_tempatureData.startswith("tempData,"):
            values = IN_tempatureData.split(',')
            motor_temp, Battery_temp_1, Battery_temp_2, Battery_temp_3, Battery_temp_4 = values[1:]
            if motor_temp == "None":
                motor_temp = ""
            if Battery_temp_1 == "None":
                Battery_temp_1 = ""
            if Battery_temp_2 == "None":
                Battery_temp_2 = ""
            if Battery_temp_3 == "None":
                Battery_temp_3 = ""
            if Battery_temp_4 == "None":
                Battery_temp_4 = ""

        if IN_cycle_analyst.startswith("CA,"):
            values = IN_cycle_analyst.split(',')
            amp_hours, voltage, current, speed, miles = values[1:]
            if amp_hours == "None":
                amp_hours = ""
            if voltage == "None":
                voltage = ""
            if current == "None":
                current = ""
            if speed == "None":
                speed = ""
            if miles == "None":
                miles = ""

    print(f'''
time:{datetime.now()} counter:{conter} \n
throttle:{throttle} Brake_Pedal:{brake_pedal} \n        
motor_temp:{motor_temp} \n  
Battery_1:{Battery_temp_1} Battery_2:{Battery_temp_2} Battery_3:{Battery_temp_3} Battery_4:{Battery_temp_4} \n  
ca_AmpHrs:{amp_hours} ca_Voltage:{voltage} ca_Current:{current} ca_Speed:{speed} ca_Miles:{miles} \n   \n  
''')