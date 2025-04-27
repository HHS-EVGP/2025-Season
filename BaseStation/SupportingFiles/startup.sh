#!/bin/bash
source /home/basestation/myenv/bin/activate
python /home/basestation/receiver.py
sleep 1
gunicorn -w 9 -b 0.0.0.0:80 webserver:app # Workers calculated by # of cores * 2 + 1
