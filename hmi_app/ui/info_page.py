"""
Information page of the HMI application.
"""
import logging
import platform
import psutil
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QGroupBox, QGridLayout, QTextEdit,
                           QTabWidget, QFrame, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QBrush, QTextCursor
from modbus.client import ModbusClient

logger = logging.getLogger(__name__)

class IOIndicator(QFrame):
    """A visual indicator for digital I/O status."""
    
    def __init__(self, parent=None):
        """Initialize the indicator."""
        super().__init__(parent)
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self._state = False
        self.setStyleSheet("background-color: gray;")
    
    def set_state(self, state):
        """Set the state of the indicator."""
        self._state = bool(state)
        if self._state:
            self.setStyleSheet("background-color: green;")
        else:
            self.setStyleSheet("background-color: gray;")
    
    def state(self):
        """Get the current state."""
        return self._state

class Alarm:
    """Represents an alarm in the system."""
    
    # Status constants
    ACTIVE = 1
    ACKNOWLEDGED = 2
    CLEARED = 3
    
    def __init__(self, alarm_id, description, timestamp=None):
        """
        Initialize a new alarm.
        
        Args:
            alarm_id: Unique identifier for the alarm
            description: Description of the alarm
            timestamp: Time when the alarm occurred (default: current time)
        """
        self.alarm_id = alarm_id
        self.description = description
        self.timestamp = timestamp or datetime.now()
        self.status = self.ACTIVE
    
    def acknowledge(self):
        """Acknowledge the alarm."""
        if self.status == self.ACTIVE:
            self.status = self.ACKNOWLEDGED
            return True
        return False
    
    def clear(self):
        """Clear the alarm if it's not active."""
        if self.status in [self.ACKNOWLEDGED, self.ACTIVE]:
            self.status = self.CLEARED
            return True
        return False
    
    def is_active(self):
        """Check if the alarm is active."""
        return self.status == self.ACTIVE
    
    def is_acknowledged(self):
        """Check if the alarm is acknowledged."""
        return self.status == self.ACKNOWLEDGED
    
    def is_cleared(self):
        """Check if the alarm is cleared."""
        return self.status == self.CLEARED
    
    def __str__(self):
        """Get a string representation of the alarm."""
        status_text = "ACTIVE" if self.is_active() else "ACKNOWLEDGED" if self.is_acknowledged() else "CLEARED"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.alarm_id}: {self.description} - {status_text}"

class InfoPage(QWidget):
    """Information page of the application."""
    
    def __init__(self, modbus_client: ModbusClient):
        """
        Initialize the information page.
        
        Args:
            modbus_client: ModbusTCP client instance
        """
        super().__init__()
        
        self.modbus_client = modbus_client
        
        # Create alarm list
        self.alarms = []
        self.alarm_history = []
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self._create_header()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create system info tab
        self.system_tab = QWidget()
        self.system_layout = QVBoxLayout(self.system_tab)
        self._create_system_info()
        self._create_plc_info()
        self._create_event_log()
        self.system_layout.addStretch()
        self.tabs.addTab(self.system_tab, "System Info")
        
        # Create I/O status tab
        self.io_tab = QWidget()
        self.io_layout = QVBoxLayout(self.io_tab)
        self._create_io_status()
        self.io_layout.addStretch()
        self.tabs.addTab(self.io_tab, "I/O Status")
        
        # Create alarm log tab
        self.alarm_tab = QWidget()
        self.alarm_layout = QVBoxLayout(self.alarm_tab)
        self._create_alarm_log()
        self.alarm_layout.addStretch()
        self.tabs.addTab(self.alarm_tab, "Alarm Log")
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
        
        # Generate sample alarms for testing
        self._generate_sample_alarms()
    
    def _create_header(self):
        """Create the header section of the UI."""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("System Information")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
    
    def _create_system_info(self):
        """Create the system information section of the UI."""
        system_group = QGroupBox("System Information")
        system_layout = QGridLayout()
        
        # System info
        hostname_label = QLabel("Hostname:")
        self.hostname_value = QLabel(platform.node())
        system_layout.addWidget(hostname_label, 0, 0)
        system_layout.addWidget(self.hostname_value, 0, 1)
        
        os_label = QLabel("Operating System:")
        self.os_value = QLabel(f"{platform.system()} {platform.release()}")
        system_layout.addWidget(os_label, 1, 0)
        system_layout.addWidget(self.os_value, 1, 1)
        
        python_label = QLabel("Python Version:")
        self.python_value = QLabel(platform.python_version())
        system_layout.addWidget(python_label, 2, 0)
        system_layout.addWidget(self.python_value, 2, 1)
        
        uptime_label = QLabel("System Uptime:")
        self.uptime_value = QLabel()
        self.update_uptime()
        system_layout.addWidget(uptime_label, 3, 0)
        system_layout.addWidget(self.uptime_value, 3, 1)
        
        cpu_label = QLabel("CPU Usage:")
        self.cpu_value = QLabel()
        system_layout.addWidget(cpu_label, 4, 0)
        system_layout.addWidget(self.cpu_value, 4, 1)
        
        memory_label = QLabel("Memory Usage:")
        self.memory_value = QLabel()
        system_layout.addWidget(memory_label, 5, 0)
        system_layout.addWidget(self.memory_value, 5, 1)
        
        system_group.setLayout(system_layout)
        self.system_layout.addWidget(system_group)
    
    def _create_plc_info(self):
        """Create the PLC information section of the UI."""
        plc_group = QGroupBox("PLC Information")
        plc_layout = QGridLayout()
        
        # PLC info
        connection_label = QLabel("Connection Status:")
        self.connection_value = QLabel("Disconnected")
        plc_layout.addWidget(connection_label, 0, 0)
        plc_layout.addWidget(self.connection_value, 0, 1)
        
        ip_label = QLabel("IP Address:")
        self.ip_value = QLabel(self.modbus_client.host)
        plc_layout.addWidget(ip_label, 1, 0)
        plc_layout.addWidget(self.ip_value, 1, 1)
        
        port_label = QLabel("Port:")
        self.port_value = QLabel(str(self.modbus_client.port))
        plc_layout.addWidget(port_label, 2, 0)
        plc_layout.addWidget(self.port_value, 2, 1)
        
        unit_label = QLabel("Unit ID:")
        self.unit_value = QLabel(str(self.modbus_client.unit_id))
        plc_layout.addWidget(unit_label, 3, 0)
        plc_layout.addWidget(self.unit_value, 3, 1)
        
        plc_group.setLayout(plc_layout)
        self.system_layout.addWidget(plc_group)
    
    def _create_event_log(self):
        """Create the event log section of the UI."""
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        self.system_layout.addWidget(log_group)
    
    def _create_io_status(self):
        """Create the I/O status section of the UI."""
        # Create inputs group
        inputs_group = QGroupBox("Digital Inputs")
        inputs_layout = QGridLayout()
        
        # Create input indicators
        self.input_indicators = []
        for i in range(8):
            label = QLabel(f"Input X{i}")
            indicator = IOIndicator()
            self.input_indicators.append(indicator)
            inputs_layout.addWidget(label, i, 0)
            inputs_layout.addWidget(indicator, i, 1)
        
        inputs_group.setLayout(inputs_layout)
        self.io_layout.addWidget(inputs_group)
        
        # Create outputs group
        outputs_group = QGroupBox("Digital Outputs")
        outputs_layout = QGridLayout()
        
        # Create output indicators
        self.output_indicators = []
        for i in range(8):
            label = QLabel(f"Output Y{i}")
            indicator = IOIndicator()
            self.output_indicators.append(indicator)
            outputs_layout.addWidget(label, i, 0)
            outputs_layout.addWidget(indicator, i, 1)
        
        outputs_group.setLayout(outputs_layout)
        self.io_layout.addWidget(outputs_group)
    
    def _create_alarm_log(self):
        """Create the alarm log section of the UI."""
        # Create alarm text display
        alarm_group = QGroupBox("Current Alarms")
        alarm_layout = QVBoxLayout()
        
        self.alarm_text = QTextEdit()
        self.alarm_text.setReadOnly(True)
        self.alarm_text.setMinimumHeight(300)
        
        alarm_layout.addWidget(self.alarm_text)
        
        alarm_group.setLayout(alarm_layout)
        self.alarm_layout.addWidget(alarm_group)
        
        # Create button group
        button_layout = QHBoxLayout()
        
        self.ack_button = QPushButton("Acknowledge")
        self.ack_button.clicked.connect(self.acknowledge_alarms)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_alarms)
        
        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(self.show_alarm_history)
        
        button_layout.addWidget(self.ack_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.history_button)
        button_layout.addStretch()
        
        self.alarm_layout.addLayout(button_layout)
    
    def add_alarm(self, alarm_id, description):
        """
        Add a new alarm to the system.
        
        Args:
            alarm_id: Unique identifier for the alarm
            description: Description of the alarm
        """
        alarm = Alarm(alarm_id, description)
        self.alarms.append(alarm)
        self.alarm_history.append(alarm)
        
        # Limit history to most recent 100 alarms
        if len(self.alarm_history) > 100:
            self.alarm_history = self.alarm_history[-100:]
        
        self.update_alarm_display()
        return alarm
    
    def acknowledge_alarms(self):
        """Acknowledge all active alarms."""
        for alarm in self.alarms:
            if alarm.is_active():
                alarm.acknowledge()
        
        self.update_alarm_display()
    
    def reset_alarms(self):
        """Clear all acknowledged alarms."""
        active_alarms = []
        for alarm in self.alarms:
            if alarm.is_active():
                active_alarms.append(alarm)
            else:
                alarm.clear()
        
        # Keep only active alarms in the current list
        self.alarms = active_alarms
        self.update_alarm_display()
    
    def show_alarm_history(self):
        """Show the alarm history."""
        self.alarm_text.clear()
        
        # Format and display alarms
        cursor = self.alarm_text.textCursor()
        
        for alarm in sorted(self.alarm_history, key=lambda a: a.timestamp, reverse=True):
            # Format based on status
            fmt = QTextCharFormat()
            if alarm.is_active():
                fmt.setForeground(QBrush(QColor("red")))
            elif alarm.is_acknowledged():
                fmt.setForeground(QBrush(QColor("yellow")))
            else:  # Cleared
                fmt.setForeground(QBrush(QColor("green")))
            
            # Add text with formatting
            cursor.insertText(f"[{alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] ", fmt)
            cursor.insertText(f"{alarm.alarm_id}: {alarm.description}", fmt)
            
            # Status indicator
            status_text = " - ACTIVE" if alarm.is_active() else " - ACKNOWLEDGED" if alarm.is_acknowledged() else " - CLEARED"
            cursor.insertText(status_text, fmt)
            
            # New line
            cursor.insertBlock()
    
    def update_alarm_display(self):
        """Update the alarm display with current alarms."""
        self.alarm_text.clear()
        
        # Get the current 10 most recent active or acknowledged alarms
        current_alarms = [a for a in self.alarms if not a.is_cleared()]
        current_alarms = sorted(current_alarms, key=lambda a: a.timestamp, reverse=True)[:10]
        
        if not current_alarms:
            self.alarm_text.setPlainText("No active alarms")
            return
        
        # Format and display alarms
        cursor = self.alarm_text.textCursor()
        
        for alarm in current_alarms:
            # Format based on status
            fmt = QTextCharFormat()
            if alarm.is_active():
                fmt.setForeground(QBrush(QColor("red")))
            elif alarm.is_acknowledged():
                fmt.setForeground(QBrush(QColor("yellow")))
            
            # Add text with formatting
            cursor.insertText(f"[{alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] ", fmt)
            cursor.insertText(f"{alarm.alarm_id}: {alarm.description}", fmt)
            
            # Status indicator
            status_text = " - ACTIVE" if alarm.is_active() else " - ACKNOWLEDGED"
            cursor.insertText(status_text, fmt)
            
            # New line
            cursor.insertBlock()
    
    def _generate_sample_alarms(self):
        """Generate some sample alarms for testing."""
        alarm_data = [
            ("ALM001", "Motor Overload - Conveyor 1"),
            ("ALM002", "High Temperature - Main Tank"),
            ("ALM003", "Low Pressure - Hydraulic System"),
            ("ALM004", "Emergency Stop Activated"),
            ("ALM005", "Communication Error - Remote I/O")
        ]
        
        for alarm_id, description in alarm_data:
            self.add_alarm(alarm_id, description)
    
    def check_plc_alarms(self):
        """Check for alarms from the PLC."""
        if not self.modbus_client.connected:
            return
        
        # Read alarm status registers (registers 600-607)
        alarm_regs = self.modbus_client.read_holding_registers(600, 8)
        if alarm_regs is not None:
            alarm_descriptions = {
                0: "Emergency Stop Pressed",
                1: "Motor Overload Fault",
                2: "High Temperature Alarm",
                3: "Low Pressure Alarm",
                4: "Communication Timeout",
                5: "Sensor Failure",
                6: "Power Supply Fault",
                7: "Safety Circuit Open"
            }
            
            for i, status in enumerate(alarm_regs):
                alarm_id = f"ALM{600+i:03d}"
                # If the alarm is active (value > 0) and not already in our list
                if status > 0 and not any(a.alarm_id == alarm_id and a.is_active() for a in self.alarms):
                    description = alarm_descriptions.get(i, f"Unknown Alarm {i}")
                    self.add_alarm(alarm_id, description)
    
    def update_values(self):
        """Update all values on the page."""
        # Update connection status
        if self.modbus_client.connected:
            self.connection_value.setText(f"Connected")
        else:
            self.connection_value.setText("Disconnected")
        
        # Update system information
        self.update_uptime()
        self.cpu_value.setText(f"{psutil.cpu_percent()}%")
        
        memory = psutil.virtual_memory()
        self.memory_value.setText(f"{memory.percent}% ({self.format_bytes(memory.used)} / {self.format_bytes(memory.total)})")
        
        # Update event log with PLC status (register 500)
        if self.modbus_client.connected:
            status_reg = self.modbus_client.read_holding_registers(500, 1)
            if status_reg is not None:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_text.append(f"[{timestamp}] PLC Status: {status_reg[0]}")
            
            # Update input indicators - Read first 8 discrete inputs (0-7)
            inputs = self.modbus_client.read_discrete_inputs(0, 8)
            if inputs is not None:
                for i, state in enumerate(inputs):
                    if i < len(self.input_indicators):
                        self.input_indicators[i].set_state(state)
            
            # Update output indicators - Read first 8 coils (0-7)
            outputs = self.modbus_client.read_coils(0, 8)
            if outputs is not None:
                for i, state in enumerate(outputs):
                    if i < len(self.output_indicators):
                        self.output_indicators[i].set_state(state)
            
            # Check for PLC alarms
            self.check_plc_alarms()
    
    def update_uptime(self):
        """Update the system uptime display."""
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now().timestamp() - uptime_seconds
        
        days, remainder = divmod(int(uptime), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
            uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        self.uptime_value.setText(uptime_str)
    
    @staticmethod
    def format_bytes(bytes_value):
        """Format bytes to a human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} PB"