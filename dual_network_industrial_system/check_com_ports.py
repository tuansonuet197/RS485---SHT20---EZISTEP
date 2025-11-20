"""
Script kiểm tra các cổng COM có sẵn trên hệ thống
Giúp xác định cổng COM nào đang khả dụng
"""
import serial.tools.list_ports

def list_available_ports():
    """Liệt kê tất cả các cổng COM có sẵn"""
    print("=" * 60)
    print("DANH SÁCH CÁC CỔNG COM KHẢ DỤNG")
    print("=" * 60)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ Không tìm thấy cổng COM nào!")
        print("\nLưu ý:")
        print("- Kiểm tra đã cắm USB-RS485 chưa")
        print("- Kiểm tra driver đã cài đặt chưa")
        return
    
    print(f"\nTìm thấy {len(ports)} cổng COM:\n")
    
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device}")
        print(f"   Mô tả: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        
        # Kiểm tra có phải USB-RS485 không
        if "USB" in port.description.upper() or "SERIAL" in port.description.upper():
            print(f"   ✅ Có thể là USB-RS485")
        print()
    
    print("=" * 60)
    print("\nHƯỚNG DẪN CẤU HÌNH:")
    print("=" * 60)
    print("1. Xác định cổng COM của thiết bị")
    print("2. Mở file: config/settings.py")
    print("3. Cập nhật:")
    print("   - SHT20_CONFIG['port'] = 'COMx'  (cho SHT20)")
    print("   - EZISTEP_CONFIG['port'] = 'COMy'  (cho Ezi-STEP)")
    print()

if __name__ == '__main__':
    list_available_ports()
    input("\nNhấn Enter để đóng...")
