"""CRC16 Modbus calculation utilities"""

def calculate_crc16_modbus(data: bytes) -> int:
    """
    Calculate CRC16 Modbus
    Polynomial: 0xA001 (reversed 0x8005)
    """
    crc = 0xFFFF
    
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    
    return crc

def append_crc(data: bytes) -> bytes:
    """Append CRC16 to data (Little Endian)"""
    crc = calculate_crc16_modbus(data)
    return data + crc.to_bytes(2, byteorder='little')

def verify_crc(data: bytes) -> bool:
    """Verify CRC16 of received data"""
    if len(data) < 3:
        return False
    
    payload = data[:-2]
    crc_received = int.from_bytes(data[-2:], byteorder='little')
    crc_calculated = calculate_crc16_modbus(payload)
    
    return crc_received == crc_calculated
