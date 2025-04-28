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

# Get the latest table
con = sqlite3.connect(app.config['dbpath'])
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'hhs_%' ORDER BY name DESC LIMIT 1")
app.config['table_name'] = cur.fetchone()[0]
print("Reading from table:", app.config['table_name'])
con.close()


# Page to serve a json with data
@app.route("/getdata")
def getdata():

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

    # Calculate current lap time
    if app.config['racing'] and timestamp is not None:
        app.config['laptime'] = timestamp - app.config['whenracestarted'] - sum(app.config['prevlaptimes'])
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
        laptime=round(app.config['laptime'], 2) if app.config['laptime'] is not None else None,
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


def calc_pace(cur):

    ### Calculate target lap time ###
    # (What speed we need to go to use our whole battery in an hour
    try:

        # Calculate the ratio of speed to current used in previus data
        # Take the average of speed and current for 5 second groups
        cur.execute("""
            SELECT AVG(speed)
            FROM {}
            WHERE time > ?
                AND laps = ?
                AND current BETWEEN 17.5 AND 18.5
        """.format(app.config['table_name']), [app.config['whenracestarted'], app.config['laps'] - 1])
        optimalSpeed = cur.fetchone()[0]

        # Find average speed over the last lap
        cur.execute(f"""
            SELECT AVG(speed)
            FROM {app.config['table_name']}
            WHERE time > (
                SELECT MAX(time)
                FROM {app.config['table_name']}
                WHERE time > ? AND laps = ?
            )
            AND time <= (
                SELECT MAX(time)
                FROM {app.config['table_name']}
                WHERE time > ? AND laps = ?
            )
        """, (app.config['whenracestarted'], app.config['laps'] - 1, app.config['whenracestarted'], app.config['laps']))
        averageSpeed = cur.fetchone()[0]

        # Get the "authoritative" lap time based on the database
        cur.execute("""
            SELECT MAX(time) - MIN(time)
            FROM {}
            WHERE time > ? AND laps IS NULL""".format(app.config['table_name']), [app.config['whenracestarted']])
        app.config['laptime'] = cur.fetchone()[0]

        # Calculate lap distance (miles)
        lapDistance = averageSpeed * app.config['laptime'] / 60

        # Calculate optimal lap time (seconds)
        app.config['targetlaptime'] = lapDistance * (optimalSpeed / 60)

        # Calculate the budget for the lap (amp hours)
        app.config['capBudget'] = (app.config['targetlaptime'] / 3600) * 18

    except Exception as e:
        print("Error calculating target lap time:", e)
        app.config['targetlaptime'] = "Error"
        app.config['capBudget'] = "Error"


# Respond to an updated variable
@app.route("/usrupdate", methods=['POST'])
def usrupdate():
    # Check if the user is authenticated
    if request.remote_addr in app.config['authedusrs']:
        command = request.get_data(as_text=True)

        # TODO flip the logic so the error message is close to the error condition
        # Then you don't need to indent so many levels; just return on error

        if command:
            con = sqlite3.connect(app.config['dbpath'])
            cur = con.cursor()

            if command == 'lap+' and app.config['racing']:
                calc_pace(cur)

                # Store the previous lap number in the database
                cur.execute("UPDATE {} SET laps = ? WHERE time > ? AND laps IS NULL".format(app.config['table_name']),
                            [app.config['whenracestarted'], app.config['laps']])
                con.commit()

                # Increment the lap number
                app.config['laps'] += 1
                app.config['prevlaptimes'].append(app.config['laptime'])
                app.config['laptime'] = 0

                return ('', 200)

            elif command == 'lap-' and app.config['racing']:

                if app.config['laps'] > 0:
                    # Remove all instances of the lap count
                    cur.execute("UPDATE {} SET laps = NULL WHERE time > ? AND laps = ?".format(app.config['table_name']),
                                (app.config['whenracestarted'], app.config['laps'],))
                    con.commit()

                    app.config['laps'] -= 1

                    # Revert the current pace to the previous lap time
                    calc_pace(cur)

                    # Remove the previus lap time from the list
                    app.config['prevlaptimes'].pop()
                    # When the lap time is calculated again, it will include the removed lap time

                return ('', 200)

            elif command == 'togglerace':
                if app.config['racing']:
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

                    cur.execute("SELECT MAX(time) FROM " + app.config['table_name'])
                    app.config['whenracestarted'] = cur.fetchone()[0]

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
    waitress.serve(app, host='0.0.0.0', port=80, threads=8)
