"""RS485 Communication Manager using PySerial"""

import serial
from typing import Optional
from utils.logger import DataLogger

class RS485Manager:
    """Manages RS485 serial communication"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.logger = DataLogger()
    
    def connect(self) -> bool:
        """Open serial port connection"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            self.logger.info(f"Connected to {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close serial port"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("RS485 disconnected")
    
    def send(self, data: bytes) -> bool:
        """Send data to RS485"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        try:
            self.serial_conn.write(data)
            return True
        except Exception as e:
            self.logger.error(f"Send error: {e}")
            return False
    
    def receive(self, length: int = 1024) -> Optional[bytes]:
        """Receive data from RS485"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return None
        
        try:
            return self.serial_conn.read(length)
        except Exception as e:
            self.logger.error(f"Receive error: {e}")
            return None
    
    def send_receive(self, data: bytes, expected_length: int = 1024) -> Optional[bytes]:
        """Send data and wait for response"""
        if self.send(data):
            return self.receive(expected_length)
        return None
    
    def clear_buffer(self):
        """Clear input/output buffers"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
    
    def change_baudrate(self, baudrate: int):
        """Change baudrate (useful for multi-device communication)"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.baudrate = baudrate
            self.baudrate = baudrate
