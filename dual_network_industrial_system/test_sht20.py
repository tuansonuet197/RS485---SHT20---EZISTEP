"""
Script test kết nối SHT20
Giúp chẩn đoán vấn đề kết nối
"""
import sys
import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

def test_sht20_connection(port='COM1', baudrate=9600, slave_id=1):
    """Test kết nối SHT20"""
    print("=" * 60)
    print("TEST KẾT NỐI CẢM BIẾN SHT20")
    print("=" * 60)
    print(f"\nThông số kết nối:")
    print(f"  - Cổng COM: {port}")
    print(f"  - Baudrate: {baudrate} bps")
    print(f"  - Slave ID: {slave_id}")
    print(f"  - Data bits: 8")
    print(f"  - Stop bits: 1")
    print(f"  - Parity: None")
    print()
    
    # Bước 1: Mở cổng COM
    print("[1/4] Đang mở cổng COM...")
    try:
        client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            stopbits=1,
            parity='N',
            timeout=2.0
        )
        
        if not client.connect():
            print(f"❌ Không thể mở cổng {port}")
            print("\nKiểm tra:")
            print("  - Đã cắm USB-RS485 chưa?")
            print("  - Cổng COM có đúng không?")
            print(f"  - Chạy 'python check_com_ports.py' để xem cổng COM")
            return False
        
        print(f"✅ Đã mở cổng {port}")
        
    except Exception as e:
        print(f"❌ Lỗi khi mở cổng: {e}")
        return False
    
    # Bước 2: Đọc thanh ghi nhiệt độ
    print("\n[2/4] Đang đọc thanh ghi nhiệt độ (0x0001)...")
    try:
        result = client.read_input_registers(
            address=0x0001,
            count=1,
            device_id=slave_id
        )
        
        if result.isError():
            print(f"❌ Lỗi Modbus: {result}")
            print("\nKiểm tra:")
            print(f"  - Slave ID có đúng {slave_id} không?")
            print(f"  - Dây A+/B- có đấu đúng không?")
            print(f"  - Nguồn 24V có cấp cho SHT20 chưa?")
        else:
            temp_raw = result.registers[0]
            temp = temp_raw / 10.0
            print(f"✅ Đọc thành công: {temp_raw} -> {temp}°C")
            
    except ModbusException as e:
        print(f"❌ Modbus Exception: {e}")
        print("\nKiểm tra:")
        print(f"  - Thiết bị có kết nối không?")
        print(f"  - Baudrate có đúng {baudrate} bps không?")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    # Bước 3: Đọc thanh ghi độ ẩm
    print("\n[3/4] Đang đọc thanh ghi độ ẩm (0x0002)...")
    try:
        result = client.read_input_registers(
            address=0x0002,
            count=1,
            device_id=slave_id
        )
        
        if result.isError():
            print(f"❌ Lỗi Modbus: {result}")
        else:
            humid_raw = result.registers[0]
            humid = humid_raw / 10.0
            print(f"✅ Đọc thành công: {humid_raw} -> {humid}%RH")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    # Bước 4: Đọc Device ID
    print("\n[4/4] Đang đọc Device ID (0x0101)...")
    try:
        result = client.read_holding_registers(
            address=0x0101,
            count=1,
            device_id=slave_id
        )
        
        if result.isError():
            print(f"❌ Lỗi Modbus: {result}")
        else:
            device_id = result.registers[0]
            print(f"✅ Device ID: {device_id}")
            
            if device_id != slave_id:
                print(f"\n⚠️  CẢNH BÁO: Device ID ({device_id}) khác Slave ID ({slave_id})")
                print(f"   -> Cập nhật SHT20_CONFIG['slave_id'] = {device_id} trong config/settings.py")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    # Đóng kết nối
    client.close()
    print("\n" + "=" * 60)
    print("TEST HOÀN TẤT")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    print("\n")
    
    # Thử với các cấu hình khác nhau
    configs = [
        {'port': 'COM1', 'baudrate': 9600, 'slave_id': 1},
        # Thêm cấu hình khác nếu cần
    ]
    
    for config in configs:
        test_sht20_connection(**config)
        print("\n")
    
    # Thử các Slave ID khác nếu ID mặc định thất bại
    print("\nThử tìm kiếm Slave ID...")
    client = ModbusSerialClient(port='COM1', baudrate=9600, timeout=0.5)
    if client.connect():
        found = False
        for slave_id in range(1, 11):  # Thử ID từ 1-10
            try:
                result = client.read_input_registers(0x0001, 1, device_id=slave_id)
                if not result.isError():
                    print(f"✅ Tìm thấy thiết bị tại Slave ID: {slave_id}")
                    found = True
                    break
            except:
                pass
        
        if not found:
            print("❌ Không tìm thấy thiết bị ở bất kỳ Slave ID nào (1-10)")
            print("\nKhả năng:")
            print("  - Thiết bị chưa được kết nối")
            print("  - Baudrate không đúng (thử 4800, 19200)")
            print("  - Dây A+/B- bị đấu ngược")
        
        client.close()
    
    input("\nNhấn Enter để đóng...")
