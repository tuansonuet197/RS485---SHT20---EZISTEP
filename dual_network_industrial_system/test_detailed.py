"""
Script test chi tiết để debug Ezi-STEP
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
    """Gửi lệnh và nhận phản hồi"""
    if data is None:
        data = []
    
    frame_type = command
    data_len = len(data)
    
    # Tạo packet
    packet = [0xAA, 0xCC, slave_id, frame_type, data_len] + data
    
    # Tính CRC
    crc = calculate_crc(bytes(packet))
    crc_low = crc & 0xFF
    crc_high = (crc >> 8) & 0xFF
    
    # Thêm CRC và kết thúc
    packet.extend([crc_low, crc_high, 0xAA, 0xEE])
    
    # Gửi
    print(f"\n📤 Gửi: {' '.join(f'{b:02X}' for b in packet)}")
    ser.write(bytes(packet))
    time.sleep(0.1)
    
    # Đọc phản hồi
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"📥 Nhận: {' '.join(f'{b:02X}' for b in response)}")
        
        if len(response) >= 9:
            status_byte = response[6]
            print(f"   Status byte: 0x{status_byte:02X} = {status_byte:08b}b")
            print(f"   - Bit 0 (MOVE): {(status_byte & 0x01) != 0}")
            print(f"   - Bit 1 (ALARM): {(status_byte & 0x02) != 0}")
            print(f"   - Bit 5 (INPOS): {(status_byte & 0x20) != 0}")
            print(f"   - Bit 7 (ACK): {(status_byte & 0x80) != 0}")
            
            if len(response) > 10:
                data_bytes = response[7:-4]
                print(f"   Data: {' '.join(f'{b:02X}' for b in data_bytes)}")
        
        return response
    else:
        print("❌ Không nhận được phản hồi")
        return None

# Kết nối
print("=" * 60)
print("TEST CHI TIẾT EZI-STEP DRIVER")
print("=" * 60)

try:
    ser = serial.Serial('COM2', 115200, timeout=1)
    print(f"✅ Kết nối COM2 @ 115200 bps")
    time.sleep(0.5)
    
    # 1. Đọc trạng thái
    print("\n" + "=" * 60)
    print("1. READ STATUS (0x0D)")
    print("=" * 60)
    send_command(ser, 2, 0x0D)
    
    # 2. ALARM RESET
    print("\n" + "=" * 60)
    print("2. ALARM RESET (0x04)")
    print("=" * 60)
    send_command(ser, 2, 0x04)
    time.sleep(0.3)
    
    # 3. Đọc lại trạng thái
    print("\n" + "=" * 60)
    print("3. READ STATUS sau ALARM RESET")
    print("=" * 60)
    send_command(ser, 2, 0x0D)
    
    # 4. SERVO ON
    print("\n" + "=" * 60)
    print("4. SERVO ON (0x83)")
    print("=" * 60)
    send_command(ser, 2, 0x83)
    time.sleep(0.3)
    
    # 5. Đọc trạng thái sau SERVO ON
    print("\n" + "=" * 60)
    print("5. READ STATUS sau SERVO ON")
    print("=" * 60)
    send_command(ser, 2, 0x0D)
    
    # 6. Đọc vị trí
    print("\n" + "=" * 60)
    print("6. READ POSITION (0x0C)")
    print("=" * 60)
    response = send_command(ser, 2, 0x0C)
    if response and len(response) >= 11:
        pos_bytes = response[7:11]
        position = struct.unpack('<i', bytes(pos_bytes))[0]
        print(f"   📍 Vị trí hiện tại: {position} pulses")
    
    # 7. SET SPEED
    print("\n" + "=" * 60)
    print("7. SET SPEED (0x57) = 10000 pps")
    print("=" * 60)
    speed = 10000
    speed_bytes = list(struct.pack('<I', speed))
    send_command(ser, 2, 0x57, speed_bytes)
    time.sleep(0.2)
    
    # 8. JOG CW
    print("\n" + "=" * 60)
    print("8. JOG CW (0x37) direction=1, speed=10000")
    print("=" * 60)
    direction = 1
    speed = 10000
    jog_data = [direction] + list(struct.pack('<I', speed))
    send_command(ser, 2, 0x37, jog_data)
    
    # 9. Đọc trạng thái sau JOG
    print("\n" + "=" * 60)
    print("9. READ STATUS sau JOG CW")
    print("=" * 60)
    time.sleep(0.5)
    send_command(ser, 2, 0x0D)
    
    # 10. STOP
    print("\n" + "=" * 60)
    print("10. STOP (0x31)")
    print("=" * 60)
    send_command(ser, 2, 0x31)
    
    ser.close()
    print("\n✅ Test hoàn tất")
    
except Exception as e:
    print(f"\n❌ LỖI: {e}")
    import traceback
    traceback.print_exc()
