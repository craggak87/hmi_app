"""
Settings page of the HMI application.
"""
import logging
import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QGroupBox, QGridLayout,
                           QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                           QFormLayout, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modbus.client import ModbusClient
from config.settings import load_config, save_config

logger = logging.getLogger(__name__)

class SettingsPage(QWidget):
    """Settings page of the application."""
    
    def __init__(self, modbus_client: ModbusClient):
        """
        Initialize the settings page.
        
        Args:
            modbus_client: ModbusTCP client instance
        """
        super().__init__()
        
        self.modbus_client = modbus_client
        self.config = load_config()
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self._create_header()
        self._create_connection_settings()
        self._create_display_settings()
        self._create_alarm_settings()
        self._create_buttons()
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
    
    def _create_header(self):
        """Create the header section of the UI."""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
    
    def _create_connection_settings(self):
        """Create the connection settings section of the UI."""
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout()
        
        # Modbus Host
        self.host_input = QLineEdit(self.config.get('modbus', {}).get('host', '127.0.0.1'))
        connection_layout.addRow("Modbus Host:", self.host_input)
        
        # Modbus Port
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.config.get('modbus', {}).get('port', 502))
        connection_layout.addRow("Modbus Port:", self.port_input)
        
        # Unit ID
        self.unit_id_input = QSpinBox()
        self.unit_id_input.setRange(1, 255)
        self.unit_id_input.setValue(self.config.get('modbus', {}).get('unit_id', 1))
        connection_layout.addRow("Unit ID:", self.unit_id_input)
        
        # Auto-reconnect
        self.auto_reconnect_input = QCheckBox()
        self.auto_reconnect_input.setChecked(self.config.get('modbus', {}).get('auto_reconnect', True))
        connection_layout.addRow("Auto Reconnect:", self.auto_reconnect_input)
        
        # Reconnect delay
        self.reconnect_delay_input = QSpinBox()
        self.reconnect_delay_input.setRange(1, 60)
        self.reconnect_delay_input.setValue(self.config.get('modbus', {}).get('reconnect_delay', 5))
        connection_layout.addRow("Reconnect Delay (s):", self.reconnect_delay_input)
        
        connection_group.setLayout(connection_layout)
        self.layout.addWidget(connection_group)
    
    def _create_display_settings(self):
        """Create the display settings section of the UI."""
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        # Refresh rate
        self.refresh_rate_input = QSpinBox()
        self.refresh_rate_input.setRange(100, 10000)
        self.refresh_rate_input.setValue(self.config.get('display', {}).get('refresh_rate', 1000))
        self.refresh_rate_input.setSingleStep(100)
        self.refresh_rate_input.setSuffix(" ms")
        display_layout.addRow("Refresh Rate:", self.refresh_rate_input)
        
        # Temperature unit
        self.temp_unit_input = QComboBox()
        self.temp_unit_input.addItems(["Celsius", "Fahrenheit"])
        current_unit = self.config.get('display', {}).get('temperature_unit', 'Celsius')
        self.temp_unit_input.setCurrentText(current_unit)
        display_layout.addRow("Temperature Unit:", self.temp_unit_input)
        
        # Pressure unit
        self.pressure_unit_input = QComboBox()
        self.pressure_unit_input.addItems(["bar", "psi", "kPa"])
        current_unit = self.config.get('display', {}).get('pressure_unit', 'bar')
        self.pressure_unit_input.setCurrentText(current_unit)
        display_layout.addRow("Pressure Unit:", self.pressure_unit_input)
        
        # Font size
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 24)
        self.font_size_input.setValue(self.config.get('display', {}).get('font_size', 12))
        display_layout.addRow("Font Size:", self.font_size_input)
        
        display_group.setLayout(display_layout)
        self.layout.addWidget(display_group)
    
    def _create_alarm_settings(self):
        """Create the alarm settings section of the UI."""
        alarm_group = QGroupBox("Alarm Settings")
        alarm_layout = QFormLayout()
        
        # High temperature alarm
        self.high_temp_input = QDoubleSpinBox()
        self.high_temp_input.setRange(0, 200)
        self.high_temp_input.setValue(self.config.get('alarms', {}).get('high_temperature', 80))
        self.high_temp_input.setSuffix(" °C")
        alarm_layout.addRow("High Temperature Alarm:", self.high_temp_input)
        
        # Low temperature alarm
        self.low_temp_input = QDoubleSpinBox()
        self.low_temp_input.setRange(-50, 100)
        self.low_temp_input.setValue(self.config.get('alarms', {}).get('low_temperature', 5))
        self.low_temp_input.setSuffix(" °C")
        alarm_layout.addRow("Low Temperature Alarm:", self.low_temp_input)
        
        # High pressure alarm
        self.high_pressure_input = QDoubleSpinBox()
        self.high_pressure_input.setRange(0, 100)
        self.high_pressure_input.setValue(self.config.get('alarms', {}).get('high_pressure', 10))
        self.high_pressure_input.setSuffix(" bar")
        alarm_layout.addRow("High Pressure Alarm:", self.high_pressure_input)
        
        # Enable alarms
        self.enable_alarms_input = QCheckBox()
        self.enable_alarms_input.setChecked(self.config.get('alarms', {}).get('enabled', True))
        alarm_layout.addRow("Enable Alarms:", self.enable_alarms_input)
        
        alarm_group.setLayout(alarm_layout)
        self.layout.addWidget(alarm_group)
    
    def _create_buttons(self):
        """Create the button section of the UI."""
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.reset_button = QPushButton("Reset to Defaults")
        
        self.save_button.clicked.connect(self.save_settings)
        self.reset_button.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_button)
        
        self.layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save the current settings."""
        # Update config dictionary with form values
        if 'modbus' not in self.config:
            self.config['modbus'] = {}
        self.config['modbus']['host'] = self.host_input.text()
        self.config['modbus']['port'] = self.port_input.value()
        self.config['modbus']['unit_id'] = self.unit_id_input.value()
        self.config['modbus']['auto_reconnect'] = self.auto_reconnect_input.isChecked()
        self.config['modbus']['reconnect_delay'] = self.reconnect_delay_input.value()
        
        if 'display' not in self.config:
            self.config['display'] = {}
        self.config['display']['refresh_rate'] = self.refresh_rate_input.value()
        self.config['display']['temperature_unit'] = self.temp_unit_input.currentText()
        self.config['display']['pressure_unit'] = self.pressure_unit_input.currentText()
        self.config['display']['font_size'] = self.font_size_input.value()
        
        if 'alarms' not in self.config:
            self.config['alarms'] = {}
        self.config['alarms']['high_temperature'] = self.high_temp_input.value()
        self.config['alarms']['low_temperature'] = self.low_temp_input.value()
        self.config['alarms']['high_pressure'] = self.high_pressure_input.value()
        self.config['alarms']['enabled'] = self.enable_alarms_input.isChecked()
        
        # Save the config
        if save_config(self.config):
            QMessageBox.information(self, "Settings Saved", 
                                  "Settings have been saved successfully.\nSome settings may require application restart.")
            
            # Update Modbus client with new connection settings
            if self.modbus_client.host != self.host_input.text() or \
               self.modbus_client.port != self.port_input.value() or \
               self.modbus_client.unit_id != self.unit_id_input.value():
                
                # Disconnect if currently connected
                if self.modbus_client.connected:
                    self.modbus_client.disconnect()
                
                # Update client settings
                self.modbus_client.host = self.host_input.text()
                self.modbus_client.port = self.port_input.value()
                self.modbus_client.unit_id = self.unit_id_input.value()
                self.modbus_client.auto_reconnect = self.auto_reconnect_input.isChecked()
                self.modbus_client.reconnect_delay = self.reconnect_delay_input.value()
                
                # Try to connect with new settings
                self.modbus_client.connect()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings.")
    
    def reset_settings(self):
        """Reset settings to default values."""
        confirm = QMessageBox.question(self, "Confirm Reset", 
                                    "Are you sure you want to reset all settings to default values?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Default settings
            default_config = {
                'modbus': {
                    'host': '127.0.0.1',
                    'port': 502,
                    'unit_id': 1,
                    'auto_reconnect': True,
                    'reconnect_delay': 5
                },
                'display': {
                    'refresh_rate': 1000,
                    'temperature_unit': 'Celsius',
                    'pressure_unit': 'bar',
                    'font_size': 12
                },
                'alarms': {
                    'high_temperature': 80,
                    'low_temperature': 5,
                    'high_pressure': 10,
                    'enabled': True
                }
            }
            
            # Update UI with default values
            self.host_input.setText(default_config['modbus']['host'])
            self.port_input.setValue(default_config['modbus']['port'])
            self.unit_id_input.setValue(default_config['modbus']['unit_id'])
            self.auto_reconnect_input.setChecked(default_config['modbus']['auto_reconnect'])
            self.reconnect_delay_input.setValue(default_config['modbus']['reconnect_delay'])
            
            self.refresh_rate_input.setValue(default_config['display']['refresh_rate'])
            self.temp_unit_input.setCurrentText(default_config['display']['temperature_unit'])
            self.pressure_unit_input.setCurrentText(default_config['display']['pressure_unit'])
            self.font_size_input.setValue(default_config['display']['font_size'])
            
            self.high_temp_input.setValue(default_config['alarms']['high_temperature'])
            self.low_temp_input.setValue(default_config['alarms']['low_temperature'])
            self.high_pressure_input.setValue(default_config['alarms']['high_pressure'])
            self.enable_alarms_input.setChecked(default_config['alarms']['enabled'])
            
            QMessageBox.information(self, "Settings Reset", 
                                   "Settings have been reset to default values.\nClick Save to apply these changes.")
    
    def update_values(self):
        """Update any dynamic values from the PLC."""
        # This page doesn't have any values that need regular updates
        pass