# EV Data Collection and Visualization System

This project is a data collection and visualization system for an Electric Vehicle (EV) using a Raspberry Pi with an RFM9x LoRa radio. The system collects data, stores it in CSV files, and visualizes it through a web interface.

## Table of Contents

- [Overview](#overview)
- [Components](#components)
  - [Python Script (`main.py`)](#python-script-mainpy)
  - [Node.js Server (`server.js`)](#nodejs-server-serverjs)
  - [Frontend Components (`front_end` directory)](#frontend-components-front_end-directory)
- [Data Flow](#data-flow)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The system collects real-time data from various sensors on the EV using a Raspberry Pi connected to an RFM9x LoRa radio. The data is processed and saved into CSV files, which are then served by a Node.js server and visualized in a web-based user interface.

## Components

### Python Script (`main.py`)

- **Purpose**: Collects data from the LoRa radio and stores it in a CSV file.
- **Functionality**:
  - Configures the LoRa radio using the `adafruit_rfm9x` library.
  - Checks for the next available file name and prepares to write data.
  - Enters an infinite loop where it:
    - Receives data packets from the LoRa radio.
    - Parses and processes incoming data.
    - Logs data to a CSV file with a timestamp and counter.
  - Provides error handling for data processing.

### Node.js Server (`server.js`)

- **Purpose**: Serves the CSV data and frontend files over HTTP.
- **Functionality**:
  - Uses the Express framework to serve static files from the `front_end` directory.
  - Provides an endpoint (`/list-files`) to list all CSV files available in the `front_end` directory.
  - Fetches and returns the most recent CSV data upon request.

### Frontend Components (`front_end` directory)

- **`index.html`**: Main HTML page for the web interface.
- **`dropdown.js`**: Handles user interaction for selecting different data views.
- **`main.js`**: Fetches the latest CSV data and updates the UI dynamically.
- **`objects.js`**: Defines classes for various data visualization components (e.g., odometers, graphs).
- **`style.css`**: CSS styles for layout and design.
- **Sample Data (`001.data.csv`)**: Example CSV file containing collected data.

## Data Flow

1. **Data Collection**: The Raspberry Pi collects data from the EV via the LoRa radio.
2. **Data Storage**: The data is processed by `main.py` and stored in CSV files.
3. **Data Serving**: The Node.js server (`server.js`) serves the CSV files and static frontend.
4. **Data Visualization**: The web interface fetches and displays the latest data dynamically for real-time monitoring.

## Installation

1. **Install necessary Python libraries**:
```bash
pip install adafruit-circuitpython-rfm9x
Set Up Node.js Server:
```

2. **Install node.js**:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 20
```

3. **Install dependencies**:
```bash
npm install express
```

## Usage

1. **Make sure that server.js is running**:
```bash
node server.js
```

2. **Run the Python Script**:
```bash
python3 main.py
```

3. **Run the Node.js server**:
Access the Web Interface:

Open a web browser and navigate to http://electric.local (or the IP address of the Raspberry Pi).


## License
This project is licensed under the MIT License. 

Also, this whole README.md file was writen by ChatGPT. 😀