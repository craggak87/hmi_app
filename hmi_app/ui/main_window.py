"""
Main application window for the HMI application.
"""
import logging
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon
from modbus.client import ModbusClient

# Import page classes
from ui.main_page import MainPage
from ui.manual_page import ManualPage
from ui.auto_page import AutoPage
from ui.info_page import InfoPage
from ui.settings_page import SettingsPage

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
        
        # Set window properties
        self.setWindowTitle("Modbus HMI Application")
        self.setGeometry(100, 100, 1024, 600)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create status bar for connection information
        self.status_label = QLabel("Not Connected")
        self.statusBar().addWidget(self.status_label)
        
        # Create connection button in the top right
        self.connection_layout = QHBoxLayout()
        self.connection_button = QPushButton("Connect")
        self.connection_button.setFixedWidth(100)
        self.connection_button.clicked.connect(self.toggle_connection)
        self.connection_layout.addStretch()
        self.connection_layout.addWidget(self.connection_button)
        self.main_layout.addLayout(self.connection_layout)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.main_page = MainPage(modbus_client)
        self.manual_page = ManualPage(modbus_client)
        self.auto_page = AutoPage(modbus_client)
        self.info_page = InfoPage(modbus_client)
        self.settings_page = SettingsPage(modbus_client)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.manual_page)
        self.stacked_widget.addWidget(self.auto_page)
        self.stacked_widget.addWidget(self.info_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        # Create navigation menu at the bottom
        self._create_navigation_menu()
        
        # Create update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_values)
        self.update_timer.start(1000)  # Update every 1000ms
        
        # Initial update
        self.update_connection_status()
    
    def _create_navigation_menu(self):
        """Create the bottom navigation menu."""
        # Create a horizontal separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)
        
        # Create navigation buttons layout
        nav_layout = QHBoxLayout()
        
        # Define button style
        button_style = """
        QPushButton {
            min-height: 50px;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:checked {
            background-color: #c0c0c0;
            border: 2px solid #808080;
        }
        """
        
        # Create navigation buttons
        self.main_button = self._create_nav_button("Main", 0)
        self.manual_button = self._create_nav_button("Manual", 1)
        self.auto_button = self._create_nav_button("Auto", 2)
        self.info_button = self._create_nav_button("Info", 3)
        self.settings_button = self._create_nav_button("Settings", 4)
        
        # Add buttons to layout
        nav_layout.addWidget(self.main_button)
        nav_layout.addWidget(self.manual_button)
        nav_layout.addWidget(self.auto_button)
        nav_layout.addWidget(self.info_button)
        nav_layout.addWidget(self.settings_button)
        
        # Apply styles to all buttons
        for button in [self.main_button, self.manual_button, self.auto_button, 
                     self.info_button, self.settings_button]:
            button.setStyleSheet(button_style)
            button.setCheckable(True)
        
        # Set initial active button
        self.main_button.setChecked(True)
        
        # Add navigation layout to main layout
        self.main_layout.addLayout(nav_layout)
    
    def _create_nav_button(self, text, page_index):
        """Create a navigation button."""
        button = QPushButton(text)
        button.clicked.connect(lambda: self.change_page(page_index))
        return button
    
    def change_page(self, index):
        """
        Change the current page.
        
        Args:
            index: Index of the page to switch to
        """
        # Update stacked widget
        self.stacked_widget.setCurrentIndex(index)
        
        # Update checked state of buttons
        buttons = [self.main_button, self.manual_button, self.auto_button, 
                 self.info_button, self.settings_button]
        
        for i, button in enumerate(buttons):
            button.setChecked(i == index)
    
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
    
    def update_values(self):
        """Update all values from the PLC."""
        # Update connection status
        self.update_connection_status()
        
        # Update current page values
        current_page = self.stacked_widget.currentWidget()
        if hasattr(current_page, 'update_values') and callable(current_page.update_values):
            current_page.update_values()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Disconnect from the PLC when closing
        if self.modbus_client.connected:
            self.modbus_client.disconnect()
        event.accept()
