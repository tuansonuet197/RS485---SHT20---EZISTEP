"""
Script test kết nối Ezi-STEP
Gửi lệnh thô và xem phản hồi
"""
import serial
import time

def test_ezistep_connection(port='COM2', baudrate=115200):
    """Test kết nối Ezi-STEP với các lệnh khác nhau"""
    print("=" * 60)
    print("TEST KẾT NỐI EZI-STEP PLUS-R")
    print("=" * 60)
    print(f"\nCổng: {port}")
    print(f"Baudrate: {baudrate} bps")
    print()
    
    try:
        # Mở cổng serial
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            stopbits=1,
            parity='N',
            timeout=1.0
        )
        
        print(f"✅ Đã mở cổng {port}")
        time.sleep(0.5)
        
        # Test 1: Gửi lệnh đơn giản - Đọc trạng thái (0x0D)
        print("\n[Test 1] Gửi lệnh đọc trạng thái (0x0D)...")
        
        # Tính CRC đơn giản
        def calc_crc(data):
            crc = 0xFFFF
            for byte in data:
                crc ^= byte
                for _ in range(8):
                    if crc & 0x0001:
                        crc = (crc >> 1) ^ 0xA001
                    else:
                        crc >>= 1
            return crc
        
        # Xây dựng gói tin: Header + ID + Frame + Len + Data + CRC + Tail
        packet_data = [0x02, 0x0D, 0x00]  # ID=2, Frame=0x0D, Len=0
        crc = calc_crc(packet_data)
        packet = bytes([0xAA, 0xCC] + packet_data + [crc & 0xFF, (crc >> 8) & 0xFF] + [0xAA, 0xEE])
        
        print(f"Gửi: {packet.hex().upper()}")
        ser.write(packet)
        
        time.sleep(0.2)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"✅ Nhận: {response.hex().upper()} ({len(response)} bytes)")
        else:
            print("❌ KHÔNG nhận được phản hồi")
        
        # Test 2: Thử với Slave ID khác nhau
        print("\n[Test 2] Thử quét Slave ID (1-5)...")
        for slave_id in range(1, 6):
            packet_data = [slave_id, 0x0D, 0x00]
            crc = calc_crc(packet_data)
            packet = bytes([0xAA, 0xCC] + packet_data + [crc & 0xFF, (crc >> 8) & 0xFF] + [0xAA, 0xEE])
            
            ser.write(packet)
            time.sleep(0.1)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"✅ Slave ID {slave_id}: {response.hex().upper()}")
                break
            else:
                print(f"   Slave ID {slave_id}: Không phản hồi")
        
        # Test 3: Thử baudrate khác
        print("\n[Test 3] Thử baudrate 9600...")
        ser.close()
        ser = serial.Serial(port=port, baudrate=9600, timeout=1.0)
        
        packet_data = [0x02, 0x0D, 0x00]
        crc = calc_crc(packet_data)
        packet = bytes([0xAA, 0xCC] + packet_data + [crc & 0xFF, (crc >> 8) & 0xFF] + [0xAA, 0xEE])
        
        ser.write(packet)
        time.sleep(0.2)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"✅ Baudrate 9600: {response.hex().upper()}")
        else:
            print("❌ Baudrate 9600: Không phản hồi")
        
        ser.close()
        
        print("\n" + "=" * 60)
        print("KẾT LUẬN:")
        print("=" * 60)
        print("\nNếu KHÔNG nhận được phản hồi nào:")
        print("  1. ❌ COM2 KHÔNG PHẢI là Ezi-STEP")
        print("  2. ❌ Ezi-STEP chưa được cấp nguồn 24V")
        print("  3. ❌ Dây A+/B- chưa kết nối hoặc sai")
        print("  4. ❌ Switch SW2 cài sai baudrate")
        print("\nNếu có phản hồi:")
        print("  ✅ Thiết bị hoạt động OK")
        print("  ➡️ Cần kiểm tra lại giao thức lệnh điều khiển")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
    
    input("\nNhấn Enter để đóng...")

if __name__ == '__main__':
    test_ezistep_connection()
