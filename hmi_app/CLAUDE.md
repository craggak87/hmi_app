# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## HMI Application Overview

This is a Human-Machine Interface (HMI) application that communicates with PLCs via ModbusTCP protocol. The application provides a graphical interface built with Python and PyQt5 to monitor and control PLC devices.

## Running the Application

To run the application:

```bash
python main.py
```

## Architecture

The application follows a modular architecture:

1. **Modbus Communication Layer** (`modbus/client.py`)
   - Handles all ModbusTCP communication with the PLC
   - Provides methods for reading/writing coils, discrete inputs, and registers
   - Manages connection state and reconnection logic

2. **Configuration System** (`config/settings.py`)
   - Loads application settings from config.json
   - Provides default configuration if no file exists
   - Handles saving configuration changes

3. **User Interface** (`ui/`)
   - `main_window.py`: Main application window with navigation
   - Page modules:
     - `main_page.py`: Overview dashboard
     - `manual_page.py`: Manual control interface
     - `auto_page.py`: Automatic control with recipes
     - `info_page.py`: System information, I/O status, and alarm management
     - `settings_page.py`: Configuration interface

4. **Application Entry Point** (`main.py`)
   - Initializes logging, configuration, ModbusTCP client, and UI

## ModbusTCP Register Mapping

The application uses the following Modbus register mapping:

- **Coils (0xxxx)**:
  - 0-7: Digital outputs (Y0-Y7)
  - 10-12: Auto mode control bits (start, stop, reset)

- **Discrete Inputs (1xxxx)**:
  - 0-7: Digital inputs (X0-X7)

- **Holding Registers (4xxxx)**:
  - 100-199: Process values
  - 300-399: Control parameters
  - 500-599: Status information
  - 600-607: Alarm status registers

## Key Features

1. **Page Navigation**
   - All pages are accessible via bottom navigation menu
   - Each page has its own update cycle to refresh data from PLC

2. **I/O Status Monitoring**
   - Real-time display of digital inputs and outputs
   - Visual indicators change colors based on I/O state

3. **Alarm Management**
   - Active alarms displayed in red
   - Acknowledged alarms displayed in yellow
   - Cleared alarms displayed in green (in history view)
   - Acknowledge, Reset, and History functions

4. **Automatic Control**
   - Recipe selection and parameter configuration
   - Process start/stop/reset functionality
   - Status and progress monitoring

## Development Notes

- The UI updates via timer callbacks to ensure real-time data
- PLC communication is handled asynchronously to prevent UI freezing
- Error handling includes reconnection logic for lost PLC connections
- The application follows a clear separation between communication, configuration, and UI layers

## Dependencies

The primary dependencies for this application are:
- PyQt5: For the graphical user interface
- pymodbus: For ModbusTCP communication
- psutil: For system information monitoring

These dependencies are listed in requirements.txt.