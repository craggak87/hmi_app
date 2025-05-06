# HMI Application

A Human-Machine Interface (HMI) application for communicating with PLCs via ModbusTCP protocol.

## Overview

This application provides a graphical interface to monitor and control PLC devices using the Modbus TCP protocol. It's built with Python and PyQt5 for the user interface.

## Features

- ModbusTCP communication with PLCs
- Real-time data display
- Control interface for sending commands to the PLC
- Configurable tag system

## Requirements

- Python 3.6+
- PyQt5
- pymodbus

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application using:

```bash
python main.py
```

## Configuration

The application can be configured by editing the `config/config.json` file. A default configuration will be created on first run.

Configuration options:

- `modbus`: Connection settings for the ModbusTCP server
  - `host`: IP address or hostname of the PLC
  - `port`: TCP port (default: 502)
  - `unit_id`: Modbus unit ID (default: 1)
  - `auto_reconnect`: Whether to automatically reconnect (default: true)
  - `reconnect_delay`: Delay in seconds between reconnection attempts

- `ui`: User interface settings
  - `title`: Window title
  - `width`, `height`: Window dimensions
  - `refresh_rate`: Data refresh rate in milliseconds

- `tags`: Tag definitions for PLC data points
  - Each tag has an address, type, and optional scaling/unit

## License

This project is licensed under the MIT License - see the LICENSE file for details.