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
dbpath = "BaseStation/EVGPTelemetry.sqlite"
authedusrs = []
authcode = "hhsevgp"  # Make this whatever you like

laps = 0
laptime = None
prevlaptimes = []

targetlaptime = None
capBudget = None

maxgpspoints = 300
racing = False
whenracestarted = None

# Set up a global connection to the socket
SOCKETPATH = "/tmp/telemSocket"
socketConn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
socketConn.connect(SOCKETPATH)
print('Connected to socket:', SOCKETPATH)

lastSocketDump = [None] * 15  # * Data columns

# Page to serve a json with data
@app.route("/getdata")
def getdata():
    global lastSocketDump, laptime, racing, whenracestarted, prevlaptimes

    # See if new data is available
    readable, _, _ = select.select([socketConn], [], [], 0)
    if readable:
        # Read data from the socket
        socketDump = socketConn.recv(1024)  # 1024 byte buffer
        data = pickle.loads(socketDump)
        lastSocketDump = data
    else:
        data = lastSocketDump

    # Unpack the data
    timestamp, throttle, brake_pedal, motor_temp, batt_1, batt_2, batt_3, batt_4, \
        amp_hours, voltage, current, speed, miles, GPS_x, GPS_y = data

    # Calculate current lap time
    if racing and timestamp is not None:
        laptime = timestamp - whenracestarted - sum(prevlaptimes)
    else:
        laptime = None

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
        laps=laps,
        laptime=round(laptime, 2) if laptime is not None else None,
        maxgpspoints=maxgpspoints,
        targetlaptime=targetlaptime,
        capBudget=capBudget,
        racing=racing
    )


# Respond to an authentication attempt
@app.route("/usrauth", methods=['POST'])
def usrauth():
    global authedusrs, authcode
    authattempt = request.get_data(as_text=True)

    if authattempt == authcode:
        if request.remote_addr not in authedusrs:
            authedusrs.append(request.remote_addr)
        return ('', 200)
    else:
        return 'Invalid authentication code', 401


def calc_pace(cur):
    global targetlaptime, capBudget, laptime, whenracestarted, laps

    ### Calculate target lap time ###
    # (What speed we need to go to use our whole battery in an hour
    try:
        # Calculate the ratio of speed to current used in previous data
        # Take the average of speed and current for 5 second groups
        cur.execute("""
            SELECT AVG(speed)
            FROM main
            WHERE time > ?
                AND laps = ?
                AND current BETWEEN 17.5 AND 18.5
        """, [whenracestarted, laps - 1])
        optimalSpeed = cur.fetchone()[0]

        # Find average speed over the last lap
        cur.execute("""
            SELECT AVG(speed)
            FROM main
            WHERE time > (
                SELECT MAX(time)
                FROM main
                WHERE time > ? AND laps = ?
            )
            AND time <= (
                SELECT MAX(time)
                FROM main
                WHERE time > ? AND laps = ?
            )
        """, (whenracestarted, laps - 1, whenracestarted, laps))
        averageSpeed = cur.fetchone()[0]

        # Get the "authoritative" lap time based on the database
        cur.execute("""
            SELECT MAX(time) - MIN(time)
            FROM main
            WHERE time > ? AND laps IS NULL""", [whenracestarted])
        laptime = cur.fetchone()[0]

        # Calculate lap distance (miles)
        lapDistance = averageSpeed * laptime / 60

        # Calculate optimal lap time (seconds)
        targetlaptime = lapDistance * (optimalSpeed / 60)

        # Calculate the budget for the lap (amp hours)
        capBudget = (targetlaptime / 3600) * 18

    except Exception as e:
        print("Error calculating target lap time:", e)
        targetlaptime = "Error"
        capBudget = "Error"


# Respond to an updated variable
@app.route("/usrupdate", methods=['POST'])
def usrupdate():
    global authedusrs, laps, laptime, prevlaptimes, racing, whenracestarted, targetlaptime, capBudget

    # Check if the user is authenticated
    if request.remote_addr in authedusrs:
        command = request.get_data(as_text=True)

        if command:
            con = sqlite3.connect(dbpath)
            cur = con.cursor()

            if command == 'lap+' and racing:
                calc_pace(cur)

                # Store the previous lap number in the database
                cur.execute("UPDATE main SET laps = ? WHERE time > ? AND laps IS NULL"
                ,[whenracestarted, laps])
                con.commit()

                # Increment the lap number
                laps += 1
                if laptime is not None:
                    prevlaptimes.append(laptime)
                laptime = 0

                return ('', 200)

            elif command == 'lap-' and racing:

                if laps > 0:
                    # Remove all instances of the lap count
                    cur.execute("UPDATE main SET laps = NULL WHERE time > ? AND laps = ?"
                                ,(whenracestarted, laps,))
                    con.commit()

                    laps -= 1

                    # Revert the current pace to the previous lap time
                    calc_pace(cur)

                    # Remove the previous lap time from the list
                    prevlaptimes.pop()

                return ('', 200)

            elif command == 'togglerace':
                if racing:
                    racing = False

                    # Reset to default values
                    laps = 0
                    laptime = None
                    prevlaptimes = []
                    targetlaptime = None
                    whenracestarted = None
                    capBudget = None

                    return ('', 200)

                else:
                    racing = True

                    cur.execute("SELECT MAX(time) FROM main")
                    whenracestarted = cur.fetchone()[0]

                    return ('', 200)

            else:
                return 'Invalid variable update command', 400
        else:
            return 'No variable update command', 400
    else:
        return 'User not authenticated', 401


# Main Dashboard page
@app.route("/")
def dashboard():
    return render_template('dashboard.html')


# Page for analyzing the car's path
@app.route("/map")
def map():
    return render_template('map.html')


# Debug page
@app.route("/debug")
def debug():
    return render_template('debug.html')


if __name__ == '__main__':
    waitress.serve(app, host='0.0.0.0', port=80, threads=8)
