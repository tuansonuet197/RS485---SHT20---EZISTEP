"""
Script ghi parameter trực tiếp qua RS485 để fix ALARM
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
    
    print(f"   📤 Gửi: {' '.join(f'{b:02X}' for b in packet)}")
    ser.write(bytes(packet))
    time.sleep(0.2)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"   📥 Nhận: {' '.join(f'{b:02X}' for b in response)}")
        if len(response) >= 7:
            status = response[6]
            alarm = (status & 0x02) != 0
            print(f"   Status: 0x{status:02X} {'[❌ALARM]' if alarm else '[✅OK]'}")
        return response
    else:
        print("   ❌ Không nhận được phản hồi")
        return None

def write_parameter(ser, slave_id, param_num, value):
    """Ghi parameter vào driver"""
    print(f"\n📝 Ghi Parameter #{param_num} = {value}")
    # Command 0x58: WRITE_PARAM
    data = list(struct.pack('<H', param_num)) + list(struct.pack('<i', value))
    response = send_command(ser, slave_id, 0x58, data)
    time.sleep(0.3)
    return response

def read_parameter(ser, slave_id, param_num):
    """Đọc parameter từ driver"""
    # Command 0x52: READ_PARAM
    data = list(struct.pack('<H', param_num))
    response = send_command(ser, slave_id, 0x52, data)
    if response and len(response) >= 11:
        value_bytes = response[7:11]
        value = struct.unpack('<i', bytes(value_bytes))[0]
        return value
    return None

def save_to_eeprom(ser, slave_id):
    """Lưu parameter vào EEPROM"""
    print(f"\n💾 SAVE TO EEPROM (0xA1)")
    # Command 0xA1: Save to EEPROM
    response = send_command(ser, slave_id, 0xA1, [])
    time.sleep(1.0)  # Đợi EEPROM ghi xong
    return response

print("=" * 70)
print("GHI PARAMETER TRỰC TIẾP QUA RS485")
print("=" * 70)

try:
    ser = serial.Serial('COM2', 115200, timeout=1)
    print("✅ Kết nối COM2 @ 115200 bps\n")
    time.sleep(0.5)
    
    slave_id = 2
    
    # === ĐỌC PARAMETER HIỆN TẠI ===
    print("\n" + "=" * 70)
    print("BƯỚC 1: ĐỌC PARAMETER HIỆN TẠI")
    print("=" * 70)
    
    params_to_check = {
        9: "Alarm Logic",
        16: "Limit Sensor Logic", 
        20: "Org Method",
        24: "Org Sensor Logic"
    }
    
    for param_num, name in params_to_check.items():
        print(f"\n📖 Đọc Parameter #{param_num} ({name})")
        value = read_parameter(ser, slave_id, param_num)
        if value is not None:
            print(f"   ✅ Giá trị hiện tại: {value}")
    
    # === GHI PARAMETER MỚI ===
    print("\n" + "=" * 70)
    print("BƯỚC 2: GHI PARAMETER MỚI")
    print("=" * 70)
    
    # Ghi các parameter cần thiết
    write_parameter(ser, slave_id, 9, 1)   # Alarm Logic = 1 (High Active)
    write_parameter(ser, slave_id, 16, 1)  # Limit Sensor Logic = 1 (High Active)
    write_parameter(ser, slave_id, 20, 0)  # Org Method = 0 (No Origin)
    write_parameter(ser, slave_id, 24, 1)  # Org Sensor Logic = 1 (High Active)
    
    # === LƯU VÀO EEPROM ===
    print("\n" + "=" * 70)
    print("BƯỚC 3: LƯU VÀO EEPROM")
    print("=" * 70)
    save_to_eeprom(ser, slave_id)
    
    # === XÁC NHẬN ===
    print("\n" + "=" * 70)
    print("BƯỚC 4: XÁC NHẬN PARAMETER SAU KHI GHI")
    print("=" * 70)
    
    for param_num, name in params_to_check.items():
        print(f"\n📖 Đọc lại Parameter #{param_num} ({name})")
        value = read_parameter(ser, slave_id, param_num)
        if value is not None:
            print(f"   ✅ Giá trị mới: {value}")
    
    # === TEST MOTOR ===
    print("\n" + "=" * 70)
    print("BƯỚC 5: TEST MOTOR")
    print("=" * 70)
    
    print("\n🔄 SERVO ON")
    send_command(ser, slave_id, 0x83)
    time.sleep(0.3)
    
    print("\n⚡ SET SPEED = 10000 pps")
    speed_bytes = list(struct.pack('<I', 10000))
    send_command(ser, slave_id, 0x57, speed_bytes)
    time.sleep(0.2)
    
    print("\n➡️ JOG CW")
    jog_data = [1] + list(struct.pack('<I', 10000))
    send_command(ser, slave_id, 0x37, jog_data)
    time.sleep(2)
    
    print("\n⏹️ STOP")
    send_command(ser, slave_id, 0x31)
    
    ser.close()
    
    print("\n" + "=" * 70)
    print("✅ HOÀN TẤT!")
    print("=" * 70)
    print("\n🔌 TẮT/BẬT LẠI NGUỒN 24V để driver load lại parameter từ EEPROM")
    print("Sau đó chạy: python main.py")
    
except Exception as e:
    print(f"\n❌ LỖI: {e}")
    import traceback
    traceback.print_exc()
