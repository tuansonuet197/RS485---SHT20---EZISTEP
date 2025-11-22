"""
Script test motor với driver đã sửa (byte stuffing + đúng packet format)
Chạy script này khi có thiết bị để kiểm tra
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

def byte_stuffing(frame_data: bytes) -> bytearray:
    """Duplicate mỗi 0xAA"""
    stuffed_data = bytearray()
    for byte in frame_data:
        stuffed_data.append(byte)
        if byte == 0xAA:
            stuffed_data.append(0xAA)
    return stuffed_data

def build_packet(slave_id, frame_type, data=b''):
    """Build packet theo chuẩn Fastech với byte stuffing"""
    HEADER = bytes([0xAA, 0x55])
    TAIL = bytes([0xAA, 0x0D])
    
    # Frame core
    frame_core = struct.pack('<B', slave_id) + struct.pack('<B', frame_type) + data
    
    # CRC
    crc_val = calculate_crc(frame_core)
    crc_bytes = struct.pack('<H', crc_val)
    
    # Byte stuffing
    data_to_stuff = frame_core + crc_bytes
    stuffed_frame_data = byte_stuffing(data_to_stuff)
    
    # Final packet
    packet = HEADER + stuffed_frame_data + TAIL
    return packet

def send_command(ser, slave_id, cmd, data=b''):
    packet = build_packet(slave_id, cmd, data)
    print(f"📤 {packet.hex().upper()}")
    ser.write(packet)
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        resp = ser.read(ser.in_waiting)
        print(f"📥 {resp.hex().upper()}")
        return resp
    print("❌ No response")
    return None

print("=" * 70)
print("TEST MOTOR VỚI DRIVER MỚI (BYTE STUFFING + CHUẨN FASTECH)")
print("=" * 70)

try:
    ser = serial.Serial('COM2', 115200, timeout=1)
    print("✅ Connected COM2\n")
    time.sleep(0.5)
    
    slave_id = 2
    
    # 1. ALARM RESET
    print("1️⃣ ALARM RESET (0x04)")
    print("-" * 70)
    send_command(ser, slave_id, 0x04)
    time.sleep(0.2)
    
    # 2. SERVO ON
    print("\n2️⃣ SERVO ON (0x83)")
    print("-" * 70)
    send_command(ser, slave_id, 0x83)
    time.sleep(0.3)
    
    # 3. MOVE VELOCITY (JOG) - Velocity=10000 pps, Direction=1 (CW)
    print("\n3️⃣ MOVE VELOCITY (0x37) - JOG CW @ 10000 pps")
    print("-" * 70)
    velocity = 10000
    direction = 1
    jog_data = struct.pack('<LB', velocity, direction)
    print(f"   Data: {jog_data.hex().upper()}")
    send_command(ser, slave_id, 0x37, jog_data)
    time.sleep(2)  # Motor quay 2 giây
    
    # 4. STOP
    print("\n4️⃣ STOP (0x31)")
    print("-" * 70)
    send_command(ser, slave_id, 0x31)
    time.sleep(0.2)
    
    # 5. SERVO OFF
    print("\n5️⃣ SERVO OFF (0x84)")
    print("-" * 70)
    send_command(ser, slave_id, 0x84)
    
    ser.close()
    
    print("\n" + "=" * 70)
    print("✅ TEST HOÀN TẤT!")
    print("=" * 70)
    print("\n🔍 KẾT QUẢ:")
    print("- Nếu motor QUAY ở bước 3 → CODE ĐÚNG! ✅")
    print("- Nếu vẫn ALARM → Kiểm tra DIP switch hoặc parameter")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

input("\nNhấn Enter để đóng...")
