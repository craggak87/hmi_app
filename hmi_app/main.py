#!/usr/bin/env python3
"""
Main application entry point for the HMI application.
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication
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
        host=config.get('modbus', {}).get('host', '127.0.0.1'),
        port=config.get('modbus', {}).get('port', 502)
    )
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    window = MainWindow(modbus_client)
    window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()