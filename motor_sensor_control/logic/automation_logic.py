"""Automation Logic Controller"""

from typing import Callable, Optional
from devices.sht20_modbus import SHT20Modbus
from devices.ezistep_driver import EziStepDriver
from utils.logger import DataLogger
import config

class AutomationController:
    """Automatic control logic based on sensor readings"""
    
    def __init__(self, sht20: SHT20Modbus, motor: EziStepDriver):
        self.sht20 = sht20
        self.motor = motor
        self.logger = DataLogger()
        
        self.auto_mode_enabled = False
        self.last_temp = None
        self.last_humidity = None
        
        # Callbacks for GUI update
        self.on_status_update: Optional[Callable] = None
    
    def enable_auto_mode(self, enable: bool = True):
        """Enable/Disable automatic mode"""
        self.auto_mode_enabled = enable
        self.logger.info(f"Auto mode {'ENABLED' if enable else 'DISABLED'}")
        
        if enable:
            # Ensure motor is enabled
            self.motor.servo_enable(True)
    
    def process_sensor_data(self, temp: float, humidity: float):
        """Process sensor data and execute control logic"""
        self.last_temp = temp
        self.last_humidity = humidity
        
        if not self.auto_mode_enabled:
            return
        
        # Temperature-based control
        if temp > config.AUTO_TEMP_HIGH:
            self.logger.warning(f"High temperature detected: {temp}°C")
            self._handle_high_temperature()
        
        elif temp < config.AUTO_TEMP_LOW:
            self.logger.warning(f"Low temperature detected: {temp}°C")
            self._handle_low_temperature()
        
        # Humidity-based control
        if humidity > config.AUTO_HUMIDITY_HIGH:
            self.logger.warning(f"High humidity detected: {humidity}%RH")
            self._handle_high_humidity()
        
        elif humidity < config.AUTO_HUMIDITY_LOW:
            self.logger.warning(f"Low humidity detected: {humidity}%RH")
            self._handle_low_humidity()
        
        # Update GUI
        if self.on_status_update:
            self.on_status_update(temp, humidity)
    
    def _handle_high_temperature(self):
        """Action when temperature is too high"""
        self.motor.move_absolute(
            position=config.MOTOR_POS_TEMP_HIGH,
            speed=config.DEFAULT_MOTOR_SPEED
        )
        self.logger.info("Moving motor to HIGH_TEMP position")
    
    def _handle_low_temperature(self):
        """Action when temperature is too low"""
        self.motor.move_absolute(
            position=config.MOTOR_POS_TEMP_LOW,
            speed=config.DEFAULT_MOTOR_SPEED
        )
        self.logger.info("Moving motor to LOW_TEMP position")
    
    def _handle_high_humidity(self):
        """Action when humidity is too high"""
        self.motor.move_absolute(
            position=config.MOTOR_POS_HUMIDITY_HIGH,
            speed=config.DEFAULT_MOTOR_SPEED
        )
        self.logger.info("Moving motor to HIGH_HUMIDITY position")
    
    def _handle_low_humidity(self):
        """Action when humidity is too low"""
        self.motor.move_absolute(
            position=config.MOTOR_POS_HUMIDITY_LOW,
            speed=config.DEFAULT_MOTOR_SPEED
        )
        self.logger.info("Moving motor to LOW_HUMIDITY position")
    
    def get_motor_status(self) -> dict:
        """Get current motor status"""
        status = self.motor.get_axis_status()
        if status:
            return {
                'position': status['position'],
                'is_moving': status['is_moving'],
                'is_homed': status['is_homed'],
                'has_error': status['has_error']
            }
        return {
            'position': 0,
            'is_moving': False,
            'is_homed': False,
            'has_error': True
        }
