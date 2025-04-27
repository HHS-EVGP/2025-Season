from flask import Flask, render_template, jsonify, request
import waitress
import time
import sqlite3
from datetime import datetime

import socket
import select
import pickle

app = Flask(__name__)

## Global variables ##
app.config['dbpath'] = "BaseStation/EVGPTelemetry.sqlite"
app.config['authedusrs'] = []

app.config['laps'] = 0
app.config['laptime'] = None
app.config['prevlaptimes'] = []

app.config['targetlaptime'] = None
app.config['capBudget'] = None

app.config['maxgpspoints'] = 300
app.config['racing'] = False
app.config['whenracestarted'] = None

# Set up a global connection the the socket
SOCKETPATH = "/tmp/telemSocket"
app.config['socketConn'] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
app.config['socketConn'].connect(SOCKETPATH)
print('Connected to socket:', SOCKETPATH)

app.config['lastSocketDump'] = [None] * 15 # * Data collumns

# Connect to the database
con = sqlite3.connect(app.config['dbpath'])
cur = con.cursor()

# Get the latest table
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'hhs_%' ORDER BY name DESC LIMIT 1")
app.config['table_name'] = cur.fetchone()[0]
print("Reading from table:", app.config['table_name'])


# Page to serve a json with data
@app.route("/getdata")
def getdata():
    # Connect db
    con = sqlite3.connect(app.config['dbpath'])
    cur = con.cursor()

    # See if new data is available
    readable, _, _ = select.select([app.config['socketConn']], [], [], 0)
    if readable:
        # Read data from the socket
        socketDump = app.config['socketConn'].recv(1024)  # 1024 byte buffer
        data = pickle.loads(socketDump)
        app.config['lastSocketDump'] = data
    else:
        data = app.config['lastSocketDump']

    # Unpack the data
    timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4, \
    amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = data

    # If racing, insert the current lap count into the database
    if app.config['racing'] == True:
        con.execute("INSERT INTO {} (time, laps) VALUES (?, ?)".format(app.config['table_name']), (timestamp, app.config['laps']))
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
        capBudget=app.config['capBudget'],
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

                    ### Calculate target lap time ###
                    # (What speed we need to go to use our whole battery in an hour
                    try:
                        con = sqlite3.connect(app.config['dbpath'])
                        cur = con.cursor()

                        # Calculate the ratio of speed to current used in previus data
                        # Take the average of speed and current for 5 second groups
                        cur.execute("""
                            SELECT AVG(speed) AS avg_speed, AVG(current) AS avg_current
                            FROM (
                                SELECT speed, current, (ROW_NUMBER() OVER (ORDER BY time) - 1) / 20 AS grp
                                FROM {}
                            )
                            GROUP BY grp
                        """.format(app.config['table_name']))

                        # History returns as [(speed, current), (speed, current), ...]
                        hisotry = cur.fetchall()

                        # Find and go with whatever speed draws the closest to 18 amps (18 amps for one hour = 18 amp hours)
                        optimalSpeed = min(hisotry, key=lambda x: abs(x[1] - 18))[0]

                        # Find average speed over the last lap
                        cur.execute(f"""
                            SELECT AVG(speed)
                            FROM {app.config['table_name']}
                            WHERE time > (
                                SELECT MAX(time)
                                FROM {app.config['table_name']}
                                WHERE laps = ?
                            )
                            AND time <= (
                                SELECT MAX(time)
                                FROM {app.config['table_name']}
                                WHERE laps = ?
                            )
                        """, (app.config['laps'] - 1, app.config['laps']))
                        averageSpeed = cur.fetchone()[0]

                        # Calculate lap distance (miles)
                        lapDistance = averageSpeed * app.config['laptime'] /60

                        # Calculate optimal lap time (seconds)
                        app.config['targetlaptime'] = lapDistance * (optimalSpeed / 60)

                        # Calculate the budget for the lap (amp hours)
                        app.config['capBudget'] = (app.config['targetlaptime'] / 3600) * 18

                        code = 200 # Success

                    except Exception as e:
                        print("Error calculating target lap time:", e)
                        app.config['targetlaptime'] = "Error"
                        app.config['capBudget'] = "Error"
                        code = 500

                    app.config['laps'] += 1
                    app.config['prevlaptimes'].append(app.config['laptime'])
                    app.config['laptime'] = 0

                return ('', code)

            elif command == 'lap-':
                if app.config['racing'] == True:

                    if app.config['laps'] > 0:
                        # Connect an instance of the db for this thread
                        con = sqlite3.connect(app.config['dbpath'])
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

                    # Reset to default values
                    app.config['laps'] = 0
                    app.config['laptime'] = None
                    app.config['prevlaptimes'] = []
                    app.config['targetlaptime'] = None
                    app.config['whenracestarted'] = None
                    app.config['capBudget'] = None

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
    waitress.serve(app, host='0.0.0.0', port=5000)
