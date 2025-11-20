"""
TEST CUỐI CÙNG - QUAY MOTOR BẰNG MỌI CÁCH CÓ THỂ
"""
import serial
import struct
import time

def calculate_crc(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def send_cmd(ser, slave_id, cmd, data=None):
    if data is None:
        data = []
    
    packet = [0xAA, 0xCC, slave_id, cmd, len(data)] + data
    crc = calculate_crc(bytes(packet))
    packet.extend([crc & 0xFF, (crc >> 8) & 0xFF, 0xAA, 0xEE])
    
    print(f"📤 {' '.join(f'{b:02X}' for b in packet)}")
    ser.write(bytes(packet))
    time.sleep(0.15)
    
    if ser.in_waiting > 0:
        resp = ser.read(ser.in_waiting)
        print(f"📥 {' '.join(f'{b:02X}' for b in resp)}")
        if len(resp) >= 7:
            st = resp[6]
            print(f"   Status: 0x{st:02X} {'[ALARM]' if (st & 0x02) else '[OK]'}")
        return resp
    print("❌ No response")
    return None

print("=" * 70)
print("TEST CUỐI CÙNG - THỬ TẤT CẢ CÁCH ĐỂ QUAY MOTOR")
print("=" * 70)

try:
    ser = serial.Serial('COM2', 115200, timeout=1)
    print("✅ Connected COM2\n")
    time.sleep(0.5)
    
    # 1. ALARM RESET
    print("\n1️⃣ ALARM RESET (0x04)")
    print("-" * 70)
    send_cmd(ser, 2, 0x04)
    time.sleep(0.3)
    
    # 2. SERVO ON
    print("\n2️⃣ SERVO ON (0x83)")
    print("-" * 70)
    send_cmd(ser, 2, 0x83)
    time.sleep(0.3)
    
    # 3. SET SPEED (thử nhiều format khác nhau)
    print("\n3️⃣ SET SPEED (0x57)")
    print("-" * 70)
    
    # Format 1: Chỉ speed (4 bytes)
    print("   Format 1: Speed only (10000 pps)")
    speed_data = list(struct.pack('<I', 10000))
    send_cmd(ser, 2, 0x57, speed_data)
    time.sleep(0.2)
    
    # 4. THỬ JOG - Format 1: Speed + Direction
    print("\n4️⃣ JOG FORMAT 1: Speed(4) + Direction(1)")
    print("-" * 70)
    speed = 10000
    direction = 1  # CW
    data = list(struct.pack('<I', speed)) + [direction]
    send_cmd(ser, 2, 0x37, data)
    time.sleep(0.5)
    
    # 5. THỬ JOG - Format 2: Direction + Speed
    print("\n5️⃣ JOG FORMAT 2: Direction(1) + Speed(4)")
    print("-" * 70)
    data = [direction] + list(struct.pack('<I', speed))
    send_cmd(ser, 2, 0x37, data)
    time.sleep(0.5)
    
    # 6. STOP
    print("\n6️⃣ STOP")
    print("-" * 70)
    send_cmd(ser, 2, 0x31)
    time.sleep(0.2)
    
    # 7. THỬ MOVE ABSOLUTE với position = 10000
    print("\n7️⃣ MOVE ABSOLUTE: Position=10000, Speed=10000")
    print("-" * 70)
    position = 10000
    speed = 10000
    data = list(struct.pack('<i', position)) + list(struct.pack('<I', speed))
    send_cmd(ser, 2, 0x38, data)
    time.sleep(1)
    
    # 8. STOP
    print("\n8️⃣ STOP")
    print("-" * 70)
    send_cmd(ser, 2, 0x31)
    time.sleep(0.2)
    
    # 9. THỬ MOVE RELATIVE với distance = 5000
    print("\n9️⃣ MOVE RELATIVE: Distance=5000, Speed=10000")
    print("-" * 70)
    distance = 5000
    speed = 10000
    data = list(struct.pack('<i', distance)) + list(struct.pack('<I', speed))
    send_cmd(ser, 2, 0x39, data)
    time.sleep(1)
    
    # 10. STOP
    print("\n🔟 STOP")
    print("-" * 70)
    send_cmd(ser, 2, 0x31)
    
    ser.close()
    
    print("\n" + "=" * 70)
    print("✅ TEST HOÀN TẤT!")
    print("=" * 70)
    print("\n🔍 PHÂN TÍCH:")
    print("- Nếu TẤT CẢ đều ALARM → vấn đề ở HARDWARE (DIP switch, alarm input)")
    print("- Nếu có 1 lệnh OK → sử dụng lệnh đó!")
    print("- Kiểm tra xem motor có RUNG/KÊNH không → nếu có = đang nhận lệnh")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

input("\nNhấn Enter để đóng...")
