#!/bin/bash
source /home/basestation/pyenv/bin/activate
python /home/basestation/receiver.py &  # run in background
sleep 1
python /home/basestation/frontend/webserver.py
