"""
Test thử FORCE HOMING để xem có bypass được không
"""
import serial
import struct
import time

def calculate_crc(data: bytes) -> int:
    """Tính CRC-16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def send_command(ser, slave_id, command, data=None):
    """Gửi lệnh"""
    if data is None:
        data = []
    
    packet = [0xAA, 0xCC, slave_id, command, len(data)] + data
    crc = calculate_crc(bytes(packet))
    packet.extend([crc & 0xFF, (crc >> 8) & 0xFF, 0xAA, 0xEE])
    
    print(f"📤 {' '.join(f'{b:02X}' for b in packet)}")
    ser.write(bytes(packet))
    time.sleep(0.15)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"📥 {' '.join(f'{b:02X}' for b in response)}")
        if len(response) >= 7:
            status = response[6]
            alarm = (status & 0x02) != 0
            print(f"   Status: 0x{status:02X} {'[❌ALARM]' if alarm else '[✅OK]'}")
        return response
    else:
        print("❌ Không nhận được phản hồi")
        return None

print("=" * 70)
print("TEST WRITE PARAMETER - SET Org Method = 0 (No Origin)")
print("=" * 70)

try:
    ser = serial.Serial('COM2', 115200, timeout=1)
    print("✅ Kết nối COM2\n")
    time.sleep(0.5)
    
    # Thử WRITE PARAMETER: Set Org Method (param #20) = 0 (No Origin)
    print("\n1. WRITE PARAMETER #20 (Org Method) = 0 (No Origin)")
    print("-" * 70)
    # Command 0x58: WRITE_PARAM
    # Data: [param_number (2 bytes), value (4 bytes)]
    param_num = 20  # Org Method
    value = 0       # No Origin
    data = list(struct.pack('<H', param_num)) + list(struct.pack('<i', value))
    send_command(ser, 2, 0x58, data)
    time.sleep(0.5)
    
    # 2. READ PARAMETER để xác nhận
    print("\n2. READ PARAMETER #20 để kiểm tra")
    print("-" * 70)
    data = list(struct.pack('<H', param_num))
    response = send_command(ser, 2, 0x52, data)
    if response and len(response) >= 11:
        value_bytes = response[7:11]
        value = struct.unpack('<i', bytes(value_bytes))[0]
        print(f"   📍 Org Method hiện tại: {value}")
    
    # 3. SERVO ON
    print("\n3. SERVO ON")
    print("-" * 70)
    send_command(ser, 2, 0x83)
    time.sleep(0.3)
    
    # 4. SET SPEED
    print("\n4. SET SPEED = 10000 pps")
    print("-" * 70)
    speed_bytes = list(struct.pack('<I', 10000))
    send_command(ser, 2, 0x57, speed_bytes)
    time.sleep(0.2)
    
    # 5. JOG
    print("\n5. JOG CW")
    print("-" * 70)
    jog_data = [1] + list(struct.pack('<I', 10000))
    send_command(ser, 2, 0x37, jog_data)
    time.sleep(1)
    
    # 6. STOP
    print("\n6. STOP")
    print("-" * 70)
    send_command(ser, 2, 0x31)
    
    ser.close()
    print("\n" + "=" * 70)
    print("✅ Test hoàn tất")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ LỖI: {e}")
    import traceback
    traceback.print_exc()
