#!/usr/bin/env python3
"""
Main application entry point for the HMI application.
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.main_window import MainWindow
from modbus.client import ModbusClient
from config.settings import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Starting HMI application")
    
    # Load configuration
    config = load_config()
    
    # Initialize ModbusTCP client
    modbus_client = ModbusClient(
        host=config.get('modbus', {}).get('host', '192.168.3.250'),
        port=config.get('modbus', {}).get('port', 502),
        unit_id=config.get('modbus', {}).get('unit_id', 1),
        auto_reconnect=config.get('modbus', {}).get('auto_reconnect', True),
        reconnect_delay=config.get('modbus', {}).get('reconnect_delay', 5)
    )
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    # Apply application style
    app.setStyle("Fusion")
    
    # Initialize main window
    window = MainWindow(modbus_client)
    window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
