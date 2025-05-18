"""
Automatic mode page of the HMI application.
"""
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QGroupBox, QGridLayout,
                           QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
from modbus.client import ModbusClient

logger = logging.getLogger(__name__)

class AutoPage(QWidget):
    """Automatic mode page of the application."""
    
    def __init__(self, modbus_client: ModbusClient):
        """
        Initialize the automatic mode page.
        
        Args:
            modbus_client: ModbusTCP client instance
        """
        super().__init__()
        
        self.modbus_client = modbus_client
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self._create_header()
        self._create_auto_controls()
        self._create_status_display()
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
    
    def _create_header(self):
        """Create the header section of the UI."""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Automatic Mode")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
    
    def _create_auto_controls(self):
        """Create the automatic control section of the UI."""
        controls_group = QGroupBox("Automatic Controls")
        controls_layout = QGridLayout()
        
        # Recipe selection
        recipe_label = QLabel("Recipe:")
        self.recipe_combo = QComboBox()
        self.recipe_combo.addItems(["Recipe 1", "Recipe 2", "Recipe 3"])
        
        controls_layout.addWidget(recipe_label, 0, 0)
        controls_layout.addWidget(self.recipe_combo, 0, 1, 1, 2)
        
        # Target temperature
        temp_label = QLabel("Target Temperature (°C):")
        self.temp_input = QLineEdit("25.0")
        self.temp_input.setValidator(QRegExpValidator(QRegExp(r"\d{1,3}(\.\d{0,1})?"), self))
        
        controls_layout.addWidget(temp_label, 1, 0)
        controls_layout.addWidget(self.temp_input, 1, 1, 1, 2)
        
        # Cycle count
        cycle_label = QLabel("Cycle Count:")
        self.cycle_input = QLineEdit("1")
        self.cycle_input.setValidator(QRegExpValidator(QRegExp(r"\d{1,3}"), self))
        
        controls_layout.addWidget(cycle_label, 2, 0)
        controls_layout.addWidget(self.cycle_input, 2, 1, 1, 2)
        
        # Control buttons
        self.start_button = QPushButton("Start Process")
        self.stop_button = QPushButton("Stop Process")
        self.reset_button = QPushButton("Reset")
        
        self.start_button.clicked.connect(self.start_auto_process)
        self.stop_button.clicked.connect(self.stop_auto_process)
        self.reset_button.clicked.connect(self.reset_auto_process)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reset_button)
        
        controls_layout.addLayout(button_layout, 3, 0, 1, 3)
        
        controls_group.setLayout(controls_layout)
        self.layout.addWidget(controls_group)
    
    def _create_status_display(self):
        """Create the status display section of the UI."""
        status_group = QGroupBox("Process Status")
        status_layout = QGridLayout()
        
        # Process status
        status_label = QLabel("Status:")
        self.status_value = QLabel("Idle")
        status_layout.addWidget(status_label, 0, 0)
        status_layout.addWidget(self.status_value, 0, 1)
        
        # Current cycle
        cycle_label = QLabel("Current Cycle:")
        self.cycle_value = QLabel("0 / 0")
        status_layout.addWidget(cycle_label, 1, 0)
        status_layout.addWidget(self.cycle_value, 1, 1)
        
        # Progress
        progress_label = QLabel("Progress:")
        self.progress_value = QLabel("0%")
        status_layout.addWidget(progress_label, 2, 0)
        status_layout.addWidget(self.progress_value, 2, 1)
        
        # Elapsed time
        time_label = QLabel("Elapsed Time:")
        self.time_value = QLabel("00:00:00")
        status_layout.addWidget(time_label, 3, 0)
        status_layout.addWidget(self.time_value, 3, 1)
        
        status_group.setLayout(status_layout)
        self.layout.addWidget(status_group)
    
    def start_auto_process(self):
        """Start the automatic process."""
        if not self.modbus_client.connected:
            return
        
        # Get parameters
        recipe_index = self.recipe_combo.currentIndex()
        target_temp = float(self.temp_input.text())
        cycle_count = int(self.cycle_input.text())
        
        # Write parameters to PLC registers
        self.modbus_client.write_register(300, recipe_index)
        self.modbus_client.write_register(301, int(target_temp * 10))  # Scale for fixed-point
        self.modbus_client.write_register(302, cycle_count)
        
        # Set the auto mode start bit (coil 10)
        if self.modbus_client.write_coil(10, True):
            logger.info("Automatic process started")
            self.status_value.setText("Running")
        else:
            logger.error("Failed to start automatic process")
    
    def stop_auto_process(self):
        """Stop the automatic process."""
        if not self.modbus_client.connected:
            return
        
        # Set the auto mode stop bit (coil 11)
        if self.modbus_client.write_coil(11, True):
            logger.info("Automatic process stopped")
            self.status_value.setText("Stopped")
        else:
            logger.error("Failed to stop automatic process")
    
    def reset_auto_process(self):
        """Reset the automatic process."""
        if not self.modbus_client.connected:
            return
        
        # Set the auto mode reset bit (coil 12)
        if self.modbus_client.write_coil(12, True):
            logger.info("Automatic process reset")
            self.status_value.setText("Idle")
            self.cycle_value.setText("0 / 0")
            self.progress_value.setText("0%")
            self.time_value.setText("00:00:00")
        else:
            logger.error("Failed to reset automatic process")
    
    def update_values(self):
        """Update all values from the PLC."""
        if not self.modbus_client.connected:
            return
        
        # Update status (register 310)
        status_reg = self.modbus_client.read_holding_registers(310, 1)
        if status_reg is not None:
            status_codes = {0: "Idle", 1: "Running", 2: "Paused", 3: "Stopped", 4: "Error"}
            status_code = status_reg[0]
            if status_code in status_codes:
                self.status_value.setText(status_codes[status_code])
            else:
                self.status_value.setText(f"Unknown ({status_code})")
        
        # Update current cycle (register 311, 312)
        cycle_regs = self.modbus_client.read_holding_registers(311, 2)
        if cycle_regs is not None:
            current_cycle = cycle_regs[0]
            total_cycles = cycle_regs[1]
            self.cycle_value.setText(f"{current_cycle} / {total_cycles}")
        
        # Update progress (register 313)
        progress_reg = self.modbus_client.read_holding_registers(313, 1)
        if progress_reg is not None:
            progress = progress_reg[0]
            self.progress_value.setText(f"{progress}%")
        
        # Update time (registers 314, 315, 316 for hours, minutes, seconds)
        time_regs = self.modbus_client.read_holding_registers(314, 3)
        if time_regs is not None:
            hours = time_regs[0]
            minutes = time_regs[1]
            seconds = time_regs[2]
            self.time_value.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
