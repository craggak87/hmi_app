"""
Main application window for the HMI application.
"""
import logging
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGroupBox, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from modbus.client import ModbusClient

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, modbus_client: ModbusClient):
        """
        Initialize the main window.
        
        Args:
            modbus_client: ModbusTCP client instance
        """
        super().__init__()
        
        self.modbus_client = modbus_client
        self.tag_values = {}
        
        # Set window properties
        self.setWindowTitle("HMI Application")
        self.setGeometry(100, 100, 1024, 768)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create status bar for connection information
        self.status_label = QLabel("Not Connected")
        self.statusBar().addWidget(self.status_label)
        
        # Create the UI components
        self._create_header()
        self._create_control_panel()
        self._create_data_display()
        
        # Create update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_values)
        self.update_timer.start(1000)  # Update every 1000ms
        
        # Initial update
        self.update_connection_status()
    
    def _create_header(self):
        """Create the header section of the UI."""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("PLC Control System")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Connection button
        self.connection_button = QPushButton("Connect")
        self.connection_button.setFixedWidth(100)
        self.connection_button.clicked.connect(self.toggle_connection)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.connection_button)
        
        self.main_layout.addLayout(header_layout)
    
    def _create_control_panel(self):
        """Create the control panel section of the UI."""
        control_group = QGroupBox("Control Panel")
        control_layout = QGridLayout()
        
        # Motor control
        motor_label = QLabel("Motor:")
        self.motor_status = QLabel("OFF")
        self.motor_toggle = QPushButton("Start")
        self.motor_toggle.clicked.connect(self.toggle_motor)
        
        # Add widgets to layout
        control_layout.addWidget(motor_label, 0, 0)
        control_layout.addWidget(self.motor_status, 0, 1)
        control_layout.addWidget(self.motor_toggle, 0, 2)
        
        # Add more controls as needed
        control_layout.setColumnStretch(3, 1)  # Add stretch to the last column
        
        control_group.setLayout(control_layout)
        self.main_layout.addWidget(control_group)
    
    def _create_data_display(self):
        """Create the data display section of the UI."""
        data_group = QGroupBox("Process Data")
        data_layout = QGridLayout()
        
        # Temperature display
        temp_label = QLabel("Temperature:")
        self.temp_value = QLabel("--.- °C")
        data_layout.addWidget(temp_label, 0, 0)
        data_layout.addWidget(self.temp_value, 0, 1)
        
        # Pressure display
        pressure_label = QLabel("Pressure:")
        self.pressure_value = QLabel("--.- bar")
        data_layout.addWidget(pressure_label, 1, 0)
        data_layout.addWidget(self.pressure_value, 1, 1)
        
        # Add more data displays as needed
        data_layout.setColumnStretch(2, 1)  # Add stretch to the last column
        
        data_group.setLayout(data_layout)
        self.main_layout.addWidget(data_group)
        
        # Add stretch to push everything to the top
        self.main_layout.addStretch()
    
    def update_connection_status(self):
        """Update the connection status display."""
        if self.modbus_client.connected:
            self.status_label.setText(f"Connected to {self.modbus_client.host}:{self.modbus_client.port}")
            self.connection_button.setText("Disconnect")
        else:
            self.status_label.setText("Not Connected")
            self.connection_button.setText("Connect")
    
    def toggle_connection(self):
        """Toggle the Modbus connection on/off."""
        if self.modbus_client.connected:
            self.modbus_client.disconnect()
        else:
            self.modbus_client.connect()
        
        self.update_connection_status()
    
    def toggle_motor(self):
        """Toggle the motor on/off."""
        if not self.modbus_client.connected:
            return
            
        # Get current motor state (coil 0)
        current_state = self.modbus_client.read_coils(0, 1)
        if current_state is None:
            logger.error("Failed to read motor state")
            return
            
        # Toggle the state
        new_state = not current_state[0]
        if self.modbus_client.write_coil(0, new_state):
            logger.info(f"Motor turned {'ON' if new_state else 'OFF'}")
            self.update_motor_display(new_state)
        else:
            logger.error("Failed to write motor state")
    
    def update_motor_display(self, state):
        """Update the motor status display."""
        if state:
            self.motor_status.setText("ON")
            self.motor_toggle.setText("Stop")
        else:
            self.motor_status.setText("OFF")
            self.motor_toggle.setText("Start")
    
    def update_values(self):
        """Update all values from the PLC."""
        if not self.modbus_client.connected:
            return
        
        # Update motor state
        motor_state = self.modbus_client.read_coils(0, 1)
        if motor_state is not None:
            self.update_motor_display(motor_state[0])
        
        # Update temperature (register 100)
        temp_reg = self.modbus_client.read_holding_registers(100, 1)
        if temp_reg is not None:
            temperature = temp_reg[0] * 0.1  # Apply scaling
            self.temp_value.setText(f"{temperature:.1f} °C")
        
        # Update pressure (register 101)
        pressure_reg = self.modbus_client.read_holding_registers(101, 1)
        if pressure_reg is not None:
            pressure = pressure_reg[0] * 0.01  # Apply scaling
            self.pressure_value.setText(f"{pressure:.2f} bar")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Disconnect from the PLC when closing
        if self.modbus_client.connected:
            self.modbus_client.disconnect()
        event.accept()