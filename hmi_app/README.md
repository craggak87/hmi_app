# HMI Application

A Human-Machine Interface (HMI) application for communicating with PLCs via ModbusTCP protocol.

## Overview

This application provides a graphical interface to monitor and control PLC devices using the Modbus TCP protocol. It's built with Python and PyQt5 for the user interface.

## Features

- ModbusTCP communication with PLCs
- Real-time data display
- Control interface for sending commands to the PLC
- Configurable tag system
- Digital I/O status monitoring
- Alarm management system with acknowledgment and history
- System information display

## Interface Tabs

The application includes several interface tabs:

- **Main**: Overview dashboard with key process information
- **Manual**: Manual control of PLC operations
- **Auto**: Automatic process control with recipe selection
- **Info**: System information, I/O status, and alarm management
  - System Info: Host information, connection status, and event log
  - I/O Status: Real-time status of digital inputs and outputs
  - Alarm Log: Active alarms with acknowledge/reset functionality and history view
- **Settings**: Application and PLC configuration

## Requirements

- Python 3.6+
- PyQt5
- pymodbus
- psutil (for system information)

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
  - `theme`: UI theme (light or dark)

- `tags`: Tag definitions for PLC data points
  - Each tag has an address, type, and optional scaling/unit

## Modbus Register Mapping

The application uses the following Modbus register mapping:

- **Coils (0xxxx)**:
  - 0-7: Digital outputs (Y0-Y7)
  - 10: Auto mode start
  - 11: Auto mode stop
  - 12: Auto mode reset

- **Discrete Inputs (1xxxx)**:
  - 0-7: Digital inputs (X0-X7)

- **Holding Registers (4xxxx)**:
  - 100-199: Process values
  - 300-399: Control parameters
  - 500-599: Status information
  - 600-607: Alarm status registers

## Alarm System

The application includes an alarm management system that allows:

- Real-time monitoring of alarm conditions from the PLC
- Visual indication of active alarms (red) and acknowledged alarms (yellow)
- Acknowledging alarms via the Acknowledge button
- Clearing resolved alarms via the Reset button
- Viewing alarm history (last 100 alarms) via the History button

## License

This project is licensed under the MIT License - see the LICENSE file for details.