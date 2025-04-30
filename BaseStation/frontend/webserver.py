from flask import Flask, render_template, jsonify, request
import waitress
import sqlite3
from datetime import datetime

import socket
import select
import pickle

app = Flask(__name__)

## Global variables ##
dbpath = "/home/basestation/EVGPTelemetry.sqlite"
authedusrs = []
authcode = "hhsevgp"  # Make this whatever you like

laps = 0
laptime = None
prev_laptimes = []

target_laptime = None
capacity_budget = None

max_gps_points = 300
racing = False
when_race_started = None

# Set up a global connection to the socket
SOCKETPATH = "/tmp/telemSocket"
socketConn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
socketConn.connect(SOCKETPATH)
print('Connected to socket:', SOCKETPATH)

lastSocketDump = [None] * 15  # * Data columns

# Function to clean up data for display
def clean_view(var):
    if var is not None:
        var = round(var, 3)
        var = format(var, ".3f") # Add trailing zeros to ensure lenth stays the same
    return var

# Page to serve a json with data
@app.route("/getdata")
def getdata():
    global lastSocketDump, laptime, racing, when_race_started, prev_laptimes

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
        laptime = timestamp - when_race_started - sum(prev_laptimes)
    else:
        laptime = None

    return jsonify(
        systime=datetime.now().strftime("%H:%M:%S"),
        timestamp=clean_view(timestamp),
        throttle=clean_view(throttle),
        brake_pedal=clean_view(brake_pedal),
        motor_temp=clean_view(motor_temp),
        batt_1=clean_view(batt_1),
        batt_2=clean_view(batt_2),
        batt_3=clean_view(batt_3),
        batt_4=clean_view(batt_4),
        amp_hours=clean_view(amp_hours),
        voltage=clean_view(voltage),
        current=clean_view(current),
        speed=clean_view(speed),
        miles=clean_view(miles),
        GPS_x=clean_view(GPS_x),
        GPS_y=clean_view(GPS_y),
        laps=laps,
        laptime=clean_view(laptime),
        maxgpspoints=max_gps_points,
        targetlaptime=clean_view(target_laptime),
        capbudget=clean_view(capacity_budget),
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
    global target_laptime, capacity_budget, laptime, when_race_started, laps

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
        """, [when_race_started, laps - 1])
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
        """, (when_race_started, laps - 1, when_race_started, laps))
        averageSpeed = cur.fetchone()[0]

        # Get the "authoritative" lap time based on the database
        cur.execute("""
            SELECT MAX(time) - MIN(time)
            FROM main
            WHERE time > ? AND laps IS NULL""", [when_race_started])
        laptime = cur.fetchone()[0]

        # Calculate lap distance (miles)
        lapDistance = averageSpeed * laptime / 60

        # Calculate optimal lap time (seconds)
        target_laptime = lapDistance * (optimalSpeed / 60)

        # Calculate the budget for the lap (amp hours)
        capacity_budget = (target_laptime / 3600) * 18

    except Exception as e:
        print("Error calculating target lap time:", e)
        target_laptime = "Error"
        capacity_budget = "Error"


# Respond to an updated variable
@app.route("/usrupdate", methods=['POST'])
def usrupdate():
    global authedusrs, laps, laptime, prev_laptimes, racing, when_race_started, target_laptime, capacity_budget, max_gps_points

    # Check if the user is authenticated
    if request.remote_addr not in authedusrs:
        return 'User not authenticated', 401
    
    command = request.get_data(as_text=True)

    # Check for command
    if not command:
        return 'No variable update command', 400
    
    con = sqlite3.connect(dbpath)
    cur = con.cursor()

    if command == 'lap+' and racing:
        calc_pace(cur)

        # Store the previous lap number in the database
        cur.execute("UPDATE main SET laps = ? WHERE time > ? AND laps IS NULL"
        ,[laps, when_race_started])
        con.commit()

        # Find the number of data points in the last lap, and use that to know when to expire points in the scatter plot
        cur.execute("""
            SELECT COUNT(*)
            FROM main
            WHERE laps = ?"""
                ,[laps])
        max_gps_points = cur.fetchone()[0]

        # Increment the lap number
        laps += 1
        if laptime is not None:
            prev_laptimes.append(laptime)
        laptime = 0

        return ('', 200)

    elif command == 'lap-' and racing:

        if laps > 0:
            # Remove all instances of the lap count
            cur.execute("UPDATE main SET laps = NULL WHERE time > ? AND laps = ?"
                        ,(when_race_started, laps,))
            con.commit()

            laps -= 1

            # Revert the current pace to the previous lap time
            calc_pace(cur)

            # Remove the previous lap time from the list
            prev_laptimes.pop()

        return ('', 200)

    elif command == 'togglerace':
        if racing:
            racing = False

            # Reset to default values
            laps = 0
            laptime = None
            prev_laptimes = []
            target_laptime = None
            when_race_started = None
            capacity_budget = None

            return ('', 200)

        else:
            racing = True

            cur.execute("SELECT MAX(time) FROM main")
            when_race_started = cur.fetchone()[0]

            return ('', 200)

    else:
        return 'Invalid variable update command', 400

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
