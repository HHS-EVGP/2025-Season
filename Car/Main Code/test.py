
import os
import time
import logging
print("I guess all of the packages loaded! (:")

# Make sure to replace with your schools ID (Whatever you want, just not the same as someone else)
school_id = "hhs"

#Setup Send LED

#Setup variables
running = True
dataR = None
conter = 0
#Setup Logging
index = 1


def UART():
    # Send output as: "CA,amp_hours,voltage,current,speed,miles"
    return f"CA,None,None,None,None,None"

def analogPull():
    data = ""
    temp_data = ""
    data += f"throttle,None|"

    data += f"brake,None|"

    # Motor Temperature
    temp_data += "None,"

    # Battery 1 Temperature
    temp_data += "None,"

    # Battery 2 Temperature
    temp_data += "None,"

    # Battery 3 Temperature
    temp_data += "None,"

    # Battery 4 Temperature
    temp_data += "None"

    data += f"tempData,{temp_data}|"

    return data


while running:

    data_2_send = f"{school_id}|" 
    data_2_send += analogPull()
    data_2_send += UART()
    
    print(data_2_send)
