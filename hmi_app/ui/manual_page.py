"""
Manual control page of the HMI application.
"""
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QGroupBox, QGridLayout, QSlider)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modbus.client import ModbusClient

logger = logging.getLogger(__name__)

class ManualPage(QWidget):
    """Manual control page of the application."""
    
    def __init__(self, modbus_client: ModbusClient):
        """
        Initialize the manual control page.
        
        Args:
            modbus_client: ModbusTCP client instance
        """
        super().__init__()
        
        self.modbus_client = modbus_client
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self._create_header()
        self._create_manual_controls()
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
    
    def _create_header(self):
        """Create the header section of the UI."""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Manual Control")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
    
    def _create_manual_controls(self):
        """Create the manual control section of the UI."""
        controls_group = QGroupBox("Manual Controls")
        controls_layout = QGridLayout()
        
        # Motor speed control
        speed_label = QLabel("Motor Speed:")
        self.speed_value = QLabel("0%")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(0)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.update_speed_value)
        
        controls_layout.addWidget(speed_label, 0, 0)
        controls_layout.addWidget(self.speed_value, 0, 1)
        controls_layout.addWidget(self.speed_slider, 0, 2)
        
        # Valve control
        valve_label = QLabel("Valve Position:")
        self.valve_value = QLabel("Closed")
        self.valve_open = QPushButton("Open")
        self.valve_close = QPushButton("Close")
        
        self.valve_open.clicked.connect(lambda: self.set_valve(True))
        self.valve_close.clicked.connect(lambda: self.set_valve(False))
        
        valve_buttons = QHBoxLayout()
        valve_buttons.addWidget(self.valve_open)
        valve_buttons.addWidget(self.valve_close)
        
        controls_layout.addWidget(valve_label, 1, 0)
        controls_layout.addWidget(self.valve_value, 1, 1)
        controls_layout.addLayout(valve_buttons, 1, 2)
        
        # Heater control
        heater_label = QLabel("Heater:")
        self.heater_value = QLabel("OFF")
        self.heater_toggle = QPushButton("Turn On")
        self.heater_toggle.clicked.connect(self.toggle_heater)
        
        controls_layout.addWidget(heater_label, 2, 0)
        controls_layout.addWidget(self.heater_value, 2, 1)
        controls_layout.addWidget(self.heater_toggle, 2, 2)
        
        controls_group.setLayout(controls_layout)
        self.layout.addWidget(controls_group)
    
    def update_speed_value(self, value):
        """Update the motor speed value display and send to PLC."""
        self.speed_value.setText(f"{value}%")
        
        if self.modbus_client.connected:
            # Write speed value to register 200
            self.modbus_client.write_register(200, value)
    
    def set_valve(self, open_valve):
        """Set the valve position."""
        if not self.modbus_client.connected:
            return
            
        # Valve control is on coil 1
        if self.modbus_client.write_coil(1, open_valve):
            self.valve_value.setText("Open" if open_valve else "Closed")
            logger.info(f"Valve {'opened' if open_valve else 'closed'}")
        else:
            logger.error("Failed to write valve state")
    
    def toggle_heater(self):
        """Toggle the heater on/off."""
        if not self.modbus_client.connected:
            return
            
        # Heater control is on coil 2
        current_state = self.modbus_client.read_coils(2, 1)
        if current_state is None:
            logger.error("Failed to read heater state")
            return
            
        # Toggle the state
        new_state = not current_state[0]
        if self.modbus_client.write_coil(2, new_state):
            logger.info(f"Heater turned {'ON' if new_state else 'OFF'}")
            self.update_heater_display(new_state)
        else:
            logger.error("Failed to write heater state")
    
    def update_heater_display(self, state):
        """Update the heater status display."""
        if state:
            self.heater_value.setText("ON")
            self.heater_toggle.setText("Turn Off")
        else:
            self.heater_value.setText("OFF")
            self.heater_toggle.setText("Turn On")
    
    def update_values(self):
        """Update all values from the PLC."""
        if not self.modbus_client.connected:
            return
        
        # Update valve state (coil 1)
        valve_state = self.modbus_client.read_coils(1, 1)
        if valve_state is not None:
            self.valve_value.setText("Open" if valve_state[0] else "Closed")
        
        # Update heater state (coil 2)
        heater_state = self.modbus_client.read_coils(2, 1)
        if heater_state is not None:
            self.update_heater_display(heater_state[0])
        
        # Update speed value (register 200)
        speed_reg = self.modbus_client.read_holding_registers(200, 1)
        if speed_reg is not None:
            self.speed_slider.setValue(speed_reg[0])
            self.speed_value.setText(f"{speed_reg[0]}%")