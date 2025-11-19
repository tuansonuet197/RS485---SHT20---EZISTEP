"""Simple test script for devices"""

import sys
sys.path.append('.')

from devices.rs485_manager import RS485Manager
from devices.sht20_modbus import SHT20Modbus
from devices.ezistep_driver import EziStepDriver
import config
import time

def test_sht20():
    """Test SHT20 sensor"""
    print("=== Testing SHT20 ===")
    rs485 = RS485Manager(config.SHT20_PORT, config.SHT20_BAUDRATE)
    
    if not rs485.connect():
        print("Failed to connect")
        return
    
    sht20 = SHT20Modbus(rs485, config.SHT20_SLAVE_ID)
    
    for i in range(5):
        data = sht20.read_temp_humidity()
        if data:
            temp, humidity = data
            print(f"Reading {i+1}: Temp={temp:.1f}°C, Humidity={humidity:.1f}%RH")
        else:
            print(f"Reading {i+1}: Failed")
        time.sleep(1)
    
    rs485.disconnect()

def test_ezistep():
    """Test Ezi-STEP motor"""
    print("\n=== Testing Ezi-STEP ===")
    rs485 = RS485Manager(config.EZISTEP_PORT, config.EZISTEP_BAUDRATE)
    
    if not rs485.connect():
        print("Failed to connect")
        return
    
    motor = EziStepDriver(rs485, config.EZISTEP_SLAVE_ID)
    
    # Get status
    status = motor.get_axis_status()
    if status:
        print(f"Position: {status['position']} pulse")
        print(f"Is moving: {status['is_moving']}")
        print(f"Is homed: {status['is_homed']}")
    
    rs485.disconnect()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'sht20':
            test_sht20()
        elif sys.argv[1] == 'motor':
            test_ezistep()
        else:
            print("Usage: python test_devices.py [sht20|motor]")
    else:
        print("Testing both devices...")
        test_sht20()
        test_ezistep()
