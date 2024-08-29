# SPDX-FileCopyrightText: 2018 Brent Rubell for Adafruit Industries
# SPDX-License-Identifier: MIT
# Wiring Check, Pi Radio w/RFM9x
# Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
# Author: Brent Rubell for Adafruit Industries

# Last updated on 1/23/2024 

import adafruit_rfm9x
import board
import busio
import csv
import os
import time
from datetime import datetime
from digitalio import DigitalInOut, Direction, Pull

# Configure RFM9x LoRa Radio
rfm9x = adafruit_rfm9x.RFM9x(busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO), DigitalInOut(board.CE1), DigitalInOut(board.D25), 433.0, high_power = True)
rfm9x.tx_power = 23

index = 1
conter = 0

# while os.path.exists(f"/home/data/front_end/{index}.data.csv"):
#     index += 1
new_file_name = f"/home/data/front_end/2.data.csv"

fieldnames = [
    'school_id','time','counter',
    'motor_temp','throttle',
    'Brake_Pedal','Battery_1','Battery_2',
    'IMU_Accel_x', 'IMU_Accel_y', 'IMU_Accel_z',
    'IMU_Gyro_x', 'IMU_Gyro_y', 'IMU_Gyro_z',
    'ca_AmpHrs','ca_Voltage','ca_Current','ca_Speed','ca_Miles'
    ]

school_ID = None

accelerometer_x = None
accelerometer_y = None
accelerometer_z = None
gyroscope_x = None
gyroscope_y = None
gyroscope_z = None

throttle = None

motor_temp = None
Battery_temp_1 = None
Battery_temp_2 = None

brake_pedal = None

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
    with open(new_file_name, 'a', newline='') as csv_file: 
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if conter == 0:
            writer.writeheader()
    
        conter += 1
        packet = None

        # check for packet rx
        packet = rfm9x.receive()
        
        if packet is None:
            print('- Waiting for PKT -')
            writer.writerow({'time':datetime.now(),'counter':conter})
        else:
            print(packet)
            try:
                current_packet = str(packet, "utf-8")
                # print(current_packet)

                pass

                try:
                    all_data = current_packet.split('|')
                    
                    school_ID, IN_throttle, IN_brake, IN_tempatureData, IN_imu, IN_cycle_analyst, IN_extra_NULL = map(str, all_data)
                    
                    print(school_ID)
                    
                    if IN_imu.startswith("imu,"):
                        values = IN_imu.split(',')
                        accelerometer_x, accelerometer_y, accelerometer_z, gyroscope_x, gyroscope_y, gyroscope_z = map(float, values[1:])
                        if accelerometer_x == "None":
                            accelerometer_x = ""
                            accelerometer_y = ""
                            accelerometer_z = ""
                            gyroscope_x = ""
                            gyroscope_y = ""
                            gyroscope_z = ""

                    if IN_tempatureData.startswith("tempatureData,"):
                        values = IN_tempatureData.split(',')
                        motor_temp, Battery_temp_1, Battery_temp_2 = map(float, values[1:])

                        if motor_temp == "None":
                            motor_temp = ""
                        if Battery_temp_1 == "None":
                            Battery_temp_1 = ""
                        if Battery_temp_2 == "None":
                            Battery_temp_2 = ""

                    if IN_brake.startswith("brake,"):
                        values = IN_brake.split(',')
                        brake_pedal = values[1:][0] # The [0] MAY cause issues... I do not know yet.
                        if brake_pedal == "None":
                            brake_pedal = ""

                    if IN_throttle.startswith("throttle,"):
                        values = IN_throttle.split(',')
                        throttle = values[1:][0] # The [0] MAY cause issues... I do not know yet.
                        if throttle == "None":
                            throttle = ""

                    if IN_cycle_analyst.startswith("CA,"):
                        values = IN_cycle_analyst.split(',')
                        try:
                            amp_hours, voltage, current, speed, miles, Other, Other = values[1:]
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
                        except:
                            pass

                except Exception as err:
                    printError(err)
                
                try:
                    writer.writerow({
                        'school_id':school_ID,'time':datetime.now(),'counter':conter,
                        'IMU_Accel_x':accelerometer_x, 'IMU_Accel_y':accelerometer_y, 'IMU_Accel_z':accelerometer_z,
                        'IMU_Gyro_x':gyroscope_x, 'IMU_Gyro_y':gyroscope_y, 'IMU_Gyro_z':gyroscope_z,
                        'Battery_1':Battery_temp_1,'Battery_2':Battery_temp_2,'Brake_Pedal':brake_pedal,
                        'ca_AmpHrs':amp_hours,'ca_Voltage':voltage,'ca_Current':current,'ca_Speed':speed,'ca_Miles':miles,
                        'motor_temp':motor_temp,'throttle':throttle
                        })
                except Exception as err:
                    printError(err)
            except Exception as err:
                printError(err)
        csv_file.close()    
    
