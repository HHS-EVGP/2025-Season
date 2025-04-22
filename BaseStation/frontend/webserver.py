from flask import Flask, render_template, jsonify, request
import time
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Global variables
app.config['authedusrs'] = []

app.config['laps'] = 0
app.config['laptime'] = None
app.config['targetlaptime'] = None
app.config['prevlaptimes'] = []

app.config['maxgpspoints'] = 300
app.config['racing'] = False
app.config['whenracestarted'] = 0

con = sqlite3.connect("BaseStation/EVGPTelemetry.sqlite")
cur = con.cursor()

# Get the latest table
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'hhs_%' ORDER BY name DESC LIMIT 1")
app.config['table_name'] = cur.fetchone()[0]
print("Reading from table:", app.config['table_name'])


# Page to serve a json with data
@app.route("/getdata")
def getdata():
    con = sqlite3.connect("BaseStation/EVGPTelemetry.sqlite")
    cur = con.cursor()


    # Get the latest data from the database
    cur.execute("SELECT * FROM {} ORDER BY time DESC LIMIT 1".format(app.config['table_name']))
    data = cur.fetchone()

    if data is None:
        print("Nothing in DB!")
        timestamp = throttle = brake_pedal = motor_temp = batt_1 = batt_2 = batt_3 = batt_4 = \
        amp_hours = voltage = current = speed = miles = GPS_x = GPS_y = None

    else:
        timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4, \
        amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = data
        
        # If racing, insert the current lap count into the database
        if app.config['racing'] == True:
            con.execute("INSERT INTO {} (timestamp, laps) VALUES (?, ?)".format(app.config['table_name']), (timestamp, app.config['laps']))
            con.commit()

    # Calculate current lap time
    if app.config['racing'] == True:
        app.config['laptime'] = round(time.time() - app.config['whenracestarted'] - sum(app.config['prevlaptimes']), 2)
    else:
        app.config['laptime'] = None

    return jsonify(
        systime=datetime.now().strftime("%H:%M:%S"),
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
        laps=app.config['laps'],
        laptime=app.config['laptime'],
        maxgpspoints=app.config['maxgpspoints'],
        targetlaptime=app.config['targetlaptime'],
        racing=app.config['racing']
    )

# Respond to an authentication attempt
@app.route("/usrauth", methods=['POST'])
def usrauth():
    authcode = "hhsevgp" # Make this whatever you like
    authattempt = request.get_data(as_text=True)

    if authattempt == authcode:
        if request.remote_addr not in app.config['authedusrs']:
            app.config['authedusrs'].append(request.remote_addr)

        return ('', 200)
    
    else:
        return 'Invalid authentication code', 401

# Respond to an updated variable
@app.route("/usrupdate", methods=['POST'])
def usrupdate():
    # Check if the user is authenticated
    if request.remote_addr in app.config['authedusrs']:
        command = request.get_data(as_text=True)

        if command:

            if command == 'lap+':
                if app.config['racing'] == True:
                    # Calculate exact lap time
                    app.config['laptime'] = time.time() - app.config['whenracestarted'] - sum(app.config['prevlaptimes'])

                    app.config['laps'] += 1
                    app.config['prevlaptimes'].append(app.config['laptime'])
                    app.config['laptime'] = 0

                return ('', 200)

            elif command == 'lap-':
                if app.config['racing'] == True:

                    if app.config['laps'] > 0:
                        # Connect an instance of the db for this thread
                        con = sqlite3.connect("BaseStation/EVGPTelemetry.sqlite")
                        cur = con.cursor()

                        # Remove all instances of the last lap count
                        cur.execute("DELETE FROM {} WHERE laps = ?".format(app.config['table_name']), (app.config['laps'],))
                        con.commit()

                        app.config['laps'] -= 1

                        # Remove the previus lapt time from the list
                        app.config['prevlaptimes'] = app.config['prevlaptimes'][:-1]
                        # When the lap time is calculated again, it will include the removed lap time

                return ('', 200)

            elif command == 'togglerace':
                if app.config['racing'] == True:
                    app.config['racing'] = False
                    app.config['laps'] = 0
                    app.config['laptime'] = None

                    return ('', 200)

                else:
                    app.config['racing'] = True
                    app.config['whenracestarted'] = time.time()

                    return ('', 200)

            else:
                return 'Invalid variable update command', 400
    
        else:
            return 'No variable update commmand', 400
    else:
        return 'User not authenticated', 401

# Main Dashboard page
@app.route("/")
def dashboard():
    return render_template('dashboard.html')

# Page for anilyzing the car's path
@app.route("/map")
def map():
    return render_template('map.html')

# Debug page
@app.route("/debug")
def debug():
    return render_template('debug.html')


if __name__ == '__main__':
    app.run()
