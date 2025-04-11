## EV Data Collection and Visualization System

This project is a data collection and visualization system for an Electric Vehicle (EV) using a two Raspberry Pis, rpitx, an rtl-sdr, and gnu radio. The pi collects data, logs it, and transmits it to a pit station. The station stores the data in an sqlite database, and visualizes it through a web interface.

### Structure

The basic structure of the system is as follows:

  - [collector.py](/Car/collector.py) receives data from various sources on the car, and transmits it using [rpitx](https://github.com/F5OEO/rpitx) and on-off keying

  - [decoder.py](/BaseStation/decoder.py) uses [gnuradio](https://gnuradio.org/) and an [rtl-sdr](https://www.rtl-sdr.com/) on the base station to decode the transmitted data, write it to an [sqlite](https://www.sqlite.org/) database.

  - A [flask](https://flask.palletsprojects.com/en/stable/) webserver reads from the database and hosts a website to display data and allow debuging in the field
    > **Note:** Currently, only the backend is finished. The webserver is coming soon!

### Prerequisites

**Car**: (Tested on pi 3b+)

  - [rpitx](https://github.com/F5OEO/rpitx) needs to be installed with the ```sendook``` file in the working directory (See their readme)
  - ```adafruit-circuitpython-ads1x15```, ```Adafruit-ADS1x15```, ```adafruit-circuitpython-lsm6ds```, and ```pyserial``` need to be installed with pip

**Base station**: (Tested on pi 3b+)
  - ```gnuradio``` needs to be installed with apt
  - flask must be installed with a virtual python enviroment. See flask's [documentation](https://flask.palletsprojects.com/en/stable/installation/#python-version)

### Hardware Needed

  - An rtl-sdr. You can get just the dongle [here](), or the dongle with an antenna kit [here]()
  - A bandpass filter
  - Gps Unit
  > More info to come about hardware stack 

### Running

> Documentation to come once webserver and services are set up

### Acknowledgements

*This project is licensed under the MIT License.*