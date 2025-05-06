"""
Configuration management for the HMI application.
"""
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "modbus": {
        "host": "127.0.0.1",
        "port": 502,
        "unit_id": 1,
        "auto_reconnect": True,
        "reconnect_delay": 5
    },
    "ui": {
        "title": "HMI Application",
        "width": 1024,
        "height": 768,
        "refresh_rate": 1000,  # ms
        "theme": "light"
    },
    "tags": {
        # Example tag definitions
        "temperature": {
            "address": 100,
            "type": "holding_register",
            "scaling": 0.1,
            "unit": "°C"
        },
        "pressure": {
            "address": 101,
            "type": "holding_register",
            "scaling": 0.01,
            "unit": "bar"
        },
        "motor_running": {
            "address": 0,
            "type": "coil"
        }
    }
}

CONFIG_FILE_PATH = "config/config.json"

def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or create default if it doesn't exist.
    
    Returns:
        Configuration dictionary
    """
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
    
    # Check if config file exists
    if not os.path.exists(CONFIG_FILE_PATH):
        logger.info("Config file not found, creating default configuration")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    # Load config from file
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.info("Using default configuration")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Configuration saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False