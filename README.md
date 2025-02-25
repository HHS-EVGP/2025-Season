## EV Data Collection and Visualization System

This project is a data collection and visualization system for an Electric Vehicle (EV) using a two Raspberry Pis, [rpitx](https://github.com/F5OEO/rpitx), an rtl-sdr, and gnu radio. The pi collects data, logs it, and transmits it to a pit station. The station stores the data in an sqlite database, and visualizes it through a web interface.

### Structure

The basic structure of the system is as follows:

  - [collector.py](/Car/collector.py) receives data from various sources on the car, and transmits it using [rpitx] (https://github.com/F5OEO/rpitx) and on-off keying

  - [decoder.py] (/Base Station/decoder.py) uses [gnuradio] (https://www.gnuradio.org/) and an [rtl-sdr](https://www.rtl-sdr.com/) on the base station to decode the transmitted data, write it to a database, and store the data in a temporary JSON

  - A node.js server hosts a website to display the data using the temporary JSON

### Prerequisites

Car: (Tested on pi 3b+)

  - [rpitx] (https://github.com/F5OEO/rpitx) needs to be installed with the ```sendook``` file in the working directory
  - ```adafruit-circuitpython-ads1x15```, ```Adafruit-ADS1x15```, ```adafruit-circuitpython-lsm6ds```, and ```pyserial``` need to be installed with pip
  - ```dos2unix``` needs to be installed with apt

Base station: (Tested on pi 3b+)
  - ```nodejs``` and ```gnuradio``` need to be installed with apt

### Running

Documentation to come once node.js is set up

### Akdnoledgements

*This project is licensed under the MIT License.*