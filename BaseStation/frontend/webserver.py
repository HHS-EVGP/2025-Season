from flask import Flask, render_template # type: ignore
import sqlite3
from datetime import datetime
import time

app = Flask(__name__)

@app.route("/")
def dashboard():
    # Link the database
    con = sqlite3.connect("BaseStation/EVGPTelemetry.sqlite")
    cur = con.cursor()

    # Get the latest table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'hhs_%' ORDER BY name DESC LIMIT 1")
    table_name = cur.fetchone()[0]
    print("Reading from table:", table_name)

    # Get the latest data from the database
    cur.execute("SELECT * FROM {} LIMIT 1".format(table_name)) # What to do if no table?
    data = cur.fetchone()

    if data is None:
        print("Noting in DB!")
        timestamp = throttle = brake_pedal = motor_temp = batt_1 = batt_2 = batt_3 = batt_4 = \
        amp_hours = voltage = current = speed = miles = GPS_x = GPS_y = GPS_z = None
    else:
        timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4, \
        amp_hours, voltage, current, speed, miles, GPS_x, GPS_y, GPS_z = data

    return render_template(
        'dashboard.html',
        timestamp=timestamp,
        throttle=throttle,
        brake_pedal=brake_pedal,
        motor_temp=motor_temp,
        batt_1=batt_1,
        batt_2=batt_2,
        batt_3=batt_3,
        batt_4=batt_4,
        amp_hours=amp_hours,
        voltage=voltage,
        current=current,
        speed=speed,
        miles=miles,
        GPS_x=GPS_x,
        GPS_y=GPS_y,
        GPS_z=GPS_z
    )

@app.route("/map")
def map():
    return render_template('map.html')

@app.route("/debug")
def debug():
    return render_template('debug.html')

if __name__ == '__main__':
    app.run() 