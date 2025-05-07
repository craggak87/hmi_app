"""
Information page of the HMI application.
"""
import logging
import platform
import psutil
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QGroupBox, QGridLayout, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modbus.client import ModbusClient

logger = logging.getLogger(__name__)

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
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self._create_header()
        self._create_system_info()
        self._create_plc_info()
        self._create_event_log()
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
    
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
        self.layout.addWidget(system_group)
    
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
        self.layout.addWidget(plc_group)
    
    def _create_event_log(self):
        """Create the event log section of the UI."""
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        self.layout.addWidget(log_group)
    
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