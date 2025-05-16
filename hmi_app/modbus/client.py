"""
ModbusTCP client implementation using pymodbus.
"""
import logging
import time
from typing import Optional, Dict, Any, List, Tuple, Union
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException, ConnectionException

logger = logging.getLogger(__name__)

class ModbusClient:
    """
    A wrapper around pymodbus ModbusTcpClient that provides higher-level functionality.
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 502, unit_id: int = 1, 
                 auto_reconnect: bool = True, reconnect_delay: int = 5):
        """
        Initialize the ModbusTCP client.
        
        Args:
            host: The IP address or hostname of the Modbus server
            port: The TCP port to connect to
            unit_id: The Modbus unit ID (slave ID)
            auto_reconnect: Whether to automatically reconnect on connection loss
            reconnect_delay: Delay in seconds between reconnection attempts
        """
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.auto_reconnect = auto_reconnect
        self.reconnect_delay = reconnect_delay
        self.client = ModbusTcpClient(host=host, port=port)
        self.connected = False
        
        # Try to connect during initialization
        self.connect()
        
    def connect(self) -> bool:
        """
        Connect to the Modbus server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connected = self.client.connect()
            if self.connected:
                logger.info(f"Connected to Modbus server at {self.host}:{self.port}")
            else:
                logger.error(f"Failed to connect to Modbus server at {self.host}:{self.port}")
            return self.connected
        except Exception as e:
            logger.error(f"Error connecting to Modbus server: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Modbus server."""
        if self.client:
            self.client.close()
        self.connected = False
        logger.info("Disconnected from Modbus server")
    
    def ensure_connected(self) -> bool:
        """
        Make sure we're connected to the server, try to reconnect if not.
        
        Returns:
            True if connected, False otherwise
        """
        if not self.connected and self.auto_reconnect:
            logger.info("Not connected, attempting to reconnect...")
            time.sleep(self.reconnect_delay)
            return self.connect()
        return self.connected
        
    def read_coils(self, address: int, count: int = 1) -> Optional[List[bool]]:
        """
        Read coils (discrete outputs) from the PLC.
        
        Args:
            address: Starting address to read from
            count: Number of coils to read
            
        Returns:
            List of boolean values, or None if the read failed
        """
        if not self.ensure_connected():
            return None
            
        try:
            result = self.client.read_coils(address, count=count, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error reading coils: {result}")
                return None
            return result.bits[:count]
        except ConnectionException:
            logger.error("Connection lost while reading coils")
            self.connected = False
            return None
        except ModbusException as e:
            logger.error(f"Modbus error reading coils: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading coils: {e}")
            return None
    
    def read_discrete_inputs(self, address: int, count: int = 1) -> Optional[List[bool]]:
        """
        Read discrete inputs from the PLC.
        
        Args:
            address: Starting address to read from
            count: Number of inputs to read
            
        Returns:
            List of boolean values, or None if the read failed
        """
        if not self.ensure_connected():
            return None
            
        try:
            result = self.client.read_discrete_inputs(address, count=count, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error reading discrete inputs: {result}")
                return None
            return result.bits[:count]
        except ConnectionException:
            logger.error("Connection lost while reading discrete inputs")
            self.connected = False
            return None
        except ModbusException as e:
            logger.error(f"Modbus error reading discrete inputs: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading discrete inputs: {e}")
            return None
    
    def read_holding_registers(self, address: int, count: int = 1) -> Optional[List[int]]:
        """
        Read holding registers from the PLC.
        
        Args:
            address: Starting address to read from
            count: Number of registers to read
            
        Returns:
            List of register values, or None if the read failed
        """
        if not self.ensure_connected():
            return None
            
        try:
            result = self.client.read_holding_registers(address, count=count, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error reading holding registers: {result}")
                return None
            return result.registers
        except ConnectionException:
            logger.error("Connection lost while reading holding registers")
            self.connected = False
            return None
        except ModbusException as e:
            logger.error(f"Modbus error reading holding registers: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading holding registers: {e}")
            return None
    
    def read_input_registers(self, address: int, count: int = 1) -> Optional[List[int]]:
        """
        Read input registers from the PLC.
        
        Args:
            address: Starting address to read from
            count: Number of registers to read
            
        Returns:
            List of register values, or None if the read failed
        """
        if not self.ensure_connected():
            return None
            
        try:
            result = self.client.read_input_registers(address, count=count, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error reading input registers: {result}")
                return None
            return result.registers
        except ConnectionException:
            logger.error("Connection lost while reading input registers")
            self.connected = False
            return None
        except ModbusException as e:
            logger.error(f"Modbus error reading input registers: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading input registers: {e}")
            return None
    
    def write_coil(self, address: int, value: bool) -> bool:
        """
        Write a single coil to the PLC.
        
        Args:
            address: Address to write to
            value: Boolean value to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_connected():
            return False
            
        try:
            result = self.client.write_coil(address, value=value, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error writing coil: {result}")
                return False
            return True
        except ConnectionException:
            logger.error("Connection lost while writing coil")
            self.connected = False
            return False
        except ModbusException as e:
            logger.error(f"Modbus error writing coil: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing coil: {e}")
            return False
    
    def write_register(self, address: int, value: int) -> bool:
        """
        Write a single register to the PLC.
        
        Args:
            address: Address to write to
            value: Integer value to write (0-65535)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_connected():
            return False
            
        try:
            result = self.client.write_register(address, value=value, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error writing register: {result}")
                return False
            return True
        except ConnectionException:
            logger.error("Connection lost while writing register")
            self.connected = False
            return False
        except ModbusException as e:
            logger.error(f"Modbus error writing register: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing register: {e}")
            return False
    
    def write_registers(self, address: int, values: List[int]) -> bool:
        """
        Write multiple registers to the PLC.
        
        Args:
            address: Starting address to write to
            values: List of integer values to write (each 0-65535)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_connected():
            return False
            
        try:
            result = self.client.write_registers(address, values=values, slave=self.unit_id)
            if result.isError():
                logger.error(f"Error writing registers: {result}")
                return False
            return True
        except ConnectionException:
            logger.error("Connection lost while writing registers")
            self.connected = False
            return False
        except ModbusException as e:
            logger.error(f"Modbus error writing registers: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing registers: {e}")
            return False
