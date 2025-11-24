# Test chuỗi lệnh di chuyển với ALARM RESET
import sys
import time
sys.path.append('c:\\Users\\Admin\\OneDrive\\Documents\\GitHub\\RS485---SHT20---EZISTEP\\dual_network_industrial_system')

from drivers.ezistep_fastech import EziStepFastechDriver
from config import EZISTEP_CONFIG

print("=" * 60)
print("  TEST CHUỖI LỆNH DI CHUYỂN")
print("=" * 60)

driver = EziStepFastechDriver(EZISTEP_CONFIG)
if driver.connect():
    print("\n✅ Đã kết nối\n")
    
    # Bước 1: Reset alarm
    print("🔧 Bước 1: ALARM RESET...")
    driver.alarm_reset()
    time.sleep(0.5)
    
    # Bước 2: Servo ON
    print("⚡ Bước 2: SERVO ON...")
    driver.servo_on()
    time.sleep(0.5)
    
    # Bước 3: Kiểm tra status
    print("\n📊 Bước 3: Kiểm tra status...")
    status = driver.read_status()
    if status:
        print(f"Status: 0x{status:08X}")
        if status & 0x00100000:
            print("✅ SERVO ON thành công")
        if status & 0x00400000:
            print("⏸ Motor đang dừng (PT_STOPPED)")
        if status & 0x08000000:
            print("🏃 Motor đang chạy (MOTIONING)")
    
    # Bước 4: Thử JOG (đã biết hoạt động)
    print("\n🏃 Bước 4: Test JOG CW @ 10000 pps...")
    input("   Nhấn ENTER để JOG 2 giây...")
    driver.jog_move(10000, direction=1)
    time.sleep(2)
    driver.stop()
    print("✅ JOG hoàn tất")
    time.sleep(0.5)
    
    # Bước 5: Thử MOVE ABSOLUTE
    print("\n🎯 Bước 5: Test MOVE ABSOLUTE → position 5000...")
    input("   Nhấn ENTER để chạy...")
    result = driver.move_absolute(5000, 10000)
    if result:
        print("✅ Lệnh ABS Move đã gửi")
        # Đợi 3 giây và kiểm tra status
        for i in range(3):
            time.sleep(1)
            status = driver.read_status()
            if status:
                if status & 0x08000000:
                    print(f"   [{i+1}s] 🏃 Motor đang chuyển động!")
                elif status & 0x00400000:
                    print(f"   [{i+1}s] ⏸ Motor đã dừng")
                    break
    else:
        print("❌ Lệnh ABS Move thất bại")
    
    # Bước 6: Thử MOVE RELATIVE
    print("\n🔄 Bước 6: Test MOVE RELATIVE +3000...")
    input("   Nhấn ENTER để chạy...")
    result = driver.move_relative(3000, 10000)
    if result:
        print("✅ Lệnh REL Move đã gửi")
        for i in range(3):
            time.sleep(1)
            status = driver.read_status()
            if status:
                if status & 0x08000000:
                    print(f"   [{i+1}s] 🏃 Motor đang chuyển động!")
                elif status & 0x00400000:
                    print(f"   [{i+1}s] ⏸ Motor đã dừng")
                    break
    else:
        print("❌ Lệnh REL Move thất bại")
    
    print("\n🛑 Bước 7: SERVO OFF...")
    driver.servo_off()
    
    driver.disconnect()
    print("\n✅ Test hoàn tất!")
else:
    print("\n❌ Không thể kết nối!")

print("\n" + "=" * 60)
