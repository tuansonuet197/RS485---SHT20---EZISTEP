"""Ezi-STEP Plus-R Motor Controller Driver"""

from typing import Optional, Dict
from devices.rs485_manager import RS485Manager
from utils.logger import DataLogger
import struct

class EziStepDriver:
    """Ezi-STEP Plus-R RS485 Driver"""
    
    # Frame Header/Tail
    HEADER = bytes([0xAA, 0xCC])
    TAIL = bytes([0xAA, 0xEE])
    
    # Frame Types (Commands)
    CMD_GET_SLAVE_INFO = 0x01
    CMD_SAVE_PARAMETERS = 0x10
    CMD_SET_PARAMETER = 0x12
    CMD_GET_PARAMETER = 0x13
    CMD_SET_IO_OUTPUT = 0x20
    CMD_GET_IO_INPUT = 0x22
    CMD_GET_IO_OUTPUT = 0x23
    CMD_SERVO_ENABLE = 0x2A
    CMD_MOVE_STOP = 0x31
    CMD_EMERGENCY_STOP = 0x32
    CMD_MOVE_ORIGIN = 0x33
    CMD_MOVE_ABS_POS = 0x34
    CMD_MOVE_INC_POS = 0x35
    CMD_MOVE_VELOCITY = 0x37
    CMD_GET_AXIS_STATUS = 0x40
    CMD_GET_ALL_STATUS = 0x43
    
    # Parameter IDs
    PARAM_PULSE_PER_REV = 0
    PARAM_MAX_SPEED = 1
    PARAM_START_SPEED = 2
    PARAM_ACCEL_TIME = 3
    PARAM_DECEL_TIME = 4
    PARAM_JOG_SPEED = 6
    
    # Status Flags
    STATUS_ERROR = 0x00000001
    STATUS_MOTIONING = 0x00000008
    STATUS_ORIGIN_OK = 0x02000000
    
    def __init__(self, rs485: RS485Manager, slave_id: int = 2):
        self.rs485 = rs485
        self.slave_id = slave_id
        self.logger = DataLogger()
    
    def _calculate_crc(self, data: bytes) -> int:
        """Calculate CRC16 with polynomial 0xA001"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _byte_stuffing(self, data: bytes) -> bytes:
        """Apply byte stuffing for 0xAA in frame data"""
        stuffed = bytearray()
        for byte in data:
            stuffed.append(byte)
            if byte == 0xAA:
                stuffed.append(0xAA)  # Insert extra 0xAA
        return bytes(stuffed)
    
    def _byte_unstuffing(self, data: bytes) -> bytes:
        """Remove byte stuffing (0xAA 0xAA -> 0xAA)"""
        unstuffed = bytearray()
        i = 0
        while i < len(data):
            unstuffed.append(data[i])
            # If current byte is 0xAA and next is also 0xAA, skip next
            if i < len(data) - 1 and data[i] == 0xAA and data[i+1] == 0xAA:
                i += 2  # Skip the stuffed 0xAA
            else:
                i += 1
        return bytes(unstuffed)
    
    def _build_frame(self, frame_type: int, data: bytes = b'') -> bytes:
        """Build Ezi-STEP frame"""
        # Frame without stuffing
        frame_data = bytes([self.slave_id, frame_type]) + data
        
        # Apply byte stuffing
        stuffed_data = self._byte_stuffing(frame_data)
        
        # Calculate CRC on stuffed data
        crc = self._calculate_crc(stuffed_data)
        crc_bytes = struct.pack('<H', crc)  # Little endian
        
        # Complete frame
        frame = self.HEADER + stuffed_data + crc_bytes + self.TAIL
        return frame
    
    def _parse_response(self, response: bytes) -> Optional[Dict]:
        """Parse response frame"""
        if not response or len(response) < 8:
            return None
        
        # Check header/tail
        if response[:2] != self.HEADER or response[-2:] != self.TAIL:
            self.logger.error("Invalid frame header/tail")
            return None
        
        # Remove header, CRC, tail
        frame_data_stuffed = response[2:-4]
        crc_received = struct.unpack('<H', response[-4:-2])[0]
        
        # Verify CRC on stuffed data
        crc_calculated = self._calculate_crc(frame_data_stuffed)
        if crc_received != crc_calculated:
            self.logger.error(f"CRC mismatch: {crc_received:04X} != {crc_calculated:04X}")
            return None
        
        # Remove byte stuffing
        frame_data = self._byte_unstuffing(frame_data_stuffed)
        
        # Parse fields
        slave_id = frame_data[0]
        frame_type = frame_data[1]
        comm_status = frame_data[2] if len(frame_data) > 2 else 0x00
        data = frame_data[3:] if len(frame_data) > 3 else b''
        
        return {
            'slave_id': slave_id,
            'frame_type': frame_type,
            'comm_status': comm_status,
            'data': data
        }
    
    def servo_enable(self, enable: bool = True) -> bool:
        """Enable/Disable servo (Motor ON/OFF)"""
        data = bytes([0x01 if enable else 0x00])
        frame = self._build_frame(self.CMD_SERVO_ENABLE, data)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info(f"Servo {'ENABLED' if enable else 'DISABLED'}")
            return True
        
        self.logger.error(f"Servo enable failed: {result}")
        return False
    
    def move_stop(self) -> bool:
        """Stop motor with deceleration"""
        frame = self._build_frame(self.CMD_MOVE_STOP)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info("Motor stopped")
            return True
        
        self.logger.error("Stop command failed")
        return False
    
    def emergency_stop(self) -> bool:
        """Emergency stop (no deceleration)"""
        frame = self._build_frame(self.CMD_EMERGENCY_STOP)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.warning("EMERGENCY STOP activated")
            return True
        
        self.logger.error("Emergency stop failed")
        return False
    
    def move_origin(self) -> bool:
        """Home the motor (return to origin)"""
        frame = self._build_frame(self.CMD_MOVE_ORIGIN)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info("Homing started...")
            return True
        
        self.logger.error("Homing command failed")
        return False
    
    def move_absolute(self, position: int, speed: int) -> bool:
        """Move to absolute position"""
        data = struct.pack('<ii', position, speed)
        frame = self._build_frame(self.CMD_MOVE_ABS_POS, data)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info(f"Moving to position {position} @ {speed} pps")
            return True
        
        self.logger.error(f"Move absolute failed")
        return False
    
    def move_relative(self, distance: int, speed: int) -> bool:
        """Move relative distance"""
        data = struct.pack('<ii', distance, speed)
        frame = self._build_frame(self.CMD_MOVE_INC_POS, data)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info(f"Moving relative {distance} pulses @ {speed} pps")
            return True
        
        self.logger.error("Move relative failed")
        return False
    
    def move_velocity(self, speed: int) -> bool:
        """Continuous velocity move (Jog)"""
        data = struct.pack('<i', speed)
        frame = self._build_frame(self.CMD_MOVE_VELOCITY, data)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info(f"Jogging at {speed} pps")
            return True
        
        self.logger.error("Jog command failed")
        return False
    
    def get_axis_status(self) -> Optional[Dict]:
        """Get axis status flags and position"""
        frame = self._build_frame(self.CMD_GET_AXIS_STATUS)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00 and len(result['data']) >= 8:
            status_flags = struct.unpack('<I', result['data'][:4])[0]
            position = struct.unpack('<i', result['data'][4:8])[0]
            
            status = {
                'flags': status_flags,
                'position': position,
                'has_error': bool(status_flags & self.STATUS_ERROR),
                'is_moving': bool(status_flags & self.STATUS_MOTIONING),
                'is_homed': bool(status_flags & self.STATUS_ORIGIN_OK)
            }
            
            return status
        
        self.logger.error("Get status failed")
        return None
    
    def set_parameter(self, param_id: int, value: int) -> bool:
        """Set parameter to RAM"""
        data = struct.pack('<Bi', param_id, value)
        frame = self._build_frame(self.CMD_SET_PARAMETER, data)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info(f"Parameter {param_id} set to {value}")
            return True
        
        self.logger.error(f"Set parameter {param_id} failed")
        return False
    
    def save_parameters(self) -> bool:
        """Save all parameters to ROM"""
        frame = self._build_frame(self.CMD_SAVE_PARAMETERS)
        response = self.rs485.send_receive(frame)
        
        result = self._parse_response(response)
        if result and result['comm_status'] == 0x00:
            self.logger.info("Parameters saved to ROM")
            return True
        
        self.logger.error("Save parameters failed")
        return False
