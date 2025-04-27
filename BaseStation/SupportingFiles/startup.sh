#!/bin/bash
source /home/basestation/myenv/bin/activate
python /home/basestation/receiver.py
sleep 1
python /home/basestation/frontend/webvserver.py
