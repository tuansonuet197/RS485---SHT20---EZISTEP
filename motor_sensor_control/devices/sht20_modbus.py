"""SHT20 Temperature & Humidity Sensor Driver (Modbus RTU)"""

from typing import Optional, Tuple
from devices.rs485_manager import RS485Manager
from utils.crc16 import append_crc, verify_crc
from utils.logger import DataLogger

class SHT20Modbus:
    """SHT20 RS485 Modbus RTU Driver"""
    
    # Modbus Function Codes
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_REGISTER = 0x06
    
    # Register Addresses
    REG_TEMPERATURE = 0x0001
    REG_HUMIDITY = 0x0002
    REG_SLAVE_ID = 0x0101
    REG_BAUDRATE = 0x0102
    
    def __init__(self, rs485: RS485Manager, slave_id: int = 1):
        self.rs485 = rs485
        self.slave_id = slave_id
        self.logger = DataLogger()
    
    def _build_modbus_frame(self, func_code: int, start_addr: int, quantity: int) -> bytes:
        """Build Modbus RTU request frame"""
        frame = bytes([
            self.slave_id,
            func_code,
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF
        ])
        return append_crc(frame)
    
    def read_temperature(self) -> Optional[float]:
        """Read temperature (°C)"""
        request = self._build_modbus_frame(self.READ_INPUT_REGISTERS, self.REG_TEMPERATURE, 1)
        response = self.rs485.send_receive(request, expected_length=7)
        
        if response and len(response) == 7 and verify_crc(response):
            if response[0] == self.slave_id and response[1] == self.READ_INPUT_REGISTERS:
                raw_value = (response[3] << 8) | response[4]
                temp = raw_value / 10.0
                self.logger.info(f"SHT20 Temperature: {temp}°C")
                return temp
        
        self.logger.error("Failed to read temperature")
        return None
    
    def read_humidity(self) -> Optional[float]:
        """Read humidity (%RH)"""
        request = self._build_modbus_frame(self.READ_INPUT_REGISTERS, self.REG_HUMIDITY, 1)
        response = self.rs485.send_receive(request, expected_length=7)
        
        if response and len(response) == 7 and verify_crc(response):
            if response[0] == self.slave_id and response[1] == self.READ_INPUT_REGISTERS:
                raw_value = (response[3] << 8) | response[4]
                humidity = raw_value / 10.0
                self.logger.info(f"SHT20 Humidity: {humidity}%RH")
                return humidity
        
        self.logger.error("Failed to read humidity")
        return None
    
    def read_temp_humidity(self) -> Optional[Tuple[float, float]]:
        """Read both temperature and humidity"""
        request = self._build_modbus_frame(self.READ_INPUT_REGISTERS, self.REG_TEMPERATURE, 2)
        response = self.rs485.send_receive(request, expected_length=9)
        
        if response and len(response) == 9 and verify_crc(response):
            if response[0] == self.slave_id and response[1] == self.READ_INPUT_REGISTERS:
                temp_raw = (response[3] << 8) | response[4]
                hum_raw = (response[5] << 8) | response[6]
                temp = temp_raw / 10.0
                humidity = hum_raw / 10.0
                self.logger.info(f"SHT20: {temp}°C, {humidity}%RH")
                return (temp, humidity)
        
        self.logger.error("Failed to read temp & humidity")
        return None
