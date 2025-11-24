# Test đọc status chi tiết của Ezi-STEP
import sys
sys.path.append('c:\\Users\\Admin\\OneDrive\\Documents\\GitHub\\RS485---SHT20---EZISTEP\\dual_network_industrial_system')

from drivers.ezistep_fastech import EziStepFastechDriver
from config import EZISTEP_CONFIG

print("=" * 60)
print("  TEST ĐỌC TRẠNG THÁI EZI-STEP MOTOR")
print("=" * 60)

driver = EziStepFastechDriver(EZISTEP_CONFIG)
if driver.connect():
    print("\n✅ Đã kết nối motor\n")
    
    print("=== KIỂM TRA TRẠNG THÁI CHI TIẾT ===")
    status = driver.read_status()
    
    if status is not None:
        print(f"\n📊 Status Flag: 0x{status:08X}")
        print(f"📊 Binary: {bin(status)}\n")
        
        # Kiểm tra từng bit lỗi (theo EZISTEP_AXISSTATUS)
        errors = []
        
        if status & 0x00000001:
            errors.append("❌ FFLAG_ERRORALL - Có lỗi chung")
        if status & 0x00000002:
            errors.append("❌ FFLAG_HWPOSILMT - Limit + phần cứng")
        if status & 0x00000004:
            errors.append("❌ FFLAG_HWNEGALMT - Limit - phần cứng")
        if status & 0x00000008:
            errors.append("⚠️ FFLAG_SWPOGILMT - Limit + phần mềm")
        if status & 0x00000010:
            errors.append("⚠️ FFLAG_SWNEGALMT - Limit - phần mềm")
        if status & 0x00000200:
            errors.append("❌ FFLAG_ERROVERSPEED - Lỗi quá tốc")
        if status & 0x00000400:
            errors.append("❌ FFLAG_ERRPOSTRACKING - Lỗi tracking vị trí")
        if status & 0x00000800:
            errors.append("❌ FFLAG_ERROVERLOAD - Lỗi quá tải")
        if status & 0x00001000:
            errors.append("❌ FFLAG_ERROVERHEAT - Lỗi quá nhiệt")
        if status & 0x00002000:
            errors.append("❌ FFLAG_ERRBACKEMF - Lỗi back EMF")
        if status & 0x00004000:
            errors.append("⚡ FFLAG_ERRMOTORPOWER - LỖI NGUỒN ĐỘNG CƠ!")
        if status & 0x00008000:
            errors.append("❌ FFLAG_ERRINPOSITION - Lỗi In-Position")
        if status & 0x00010000:
            errors.append("🛑 FFLAG_EMGSTOP - Emergency Stop")
        if status & 0x00020000:
            errors.append("⏸ FFLAG_SLOWSTOP - Slow Stop")
        if status & 0x00040000:
            errors.append("🏠 FFLAG_ORIGINRETURNING - Đang về home")
        if status & 0x00080000:
            errors.append("✅ FFLAG_INPOSITION - Đã đến vị trí")
        if status & 0x00100000:
            errors.append("✅ FFLAG_SERVOON - Servo đang ON")
        if status & 0x00200000:
            errors.append("🔧 FFLAG_ALARMRESET - Đã reset alarm")
        if status & 0x00400000:
            errors.append("⏸ FFLAG_PTSTOPPED - Motor đã dừng (PT Stop)")
        if status & 0x00800000:
            errors.append("📍 FFLAG_ORIGINSENSOR - Origin sensor active")
        if status & 0x01000000:
            errors.append("📍 FFLAG_ZPULSE - Z-pulse active")
        if status & 0x02000000:
            errors.append("✅ FFLAG_ORIGINRETOK - Origin return OK")
        if status & 0x04000000:
            errors.append("➡️ FFLAG_MOTIONDIR - Hướng CW")
        if status & 0x08000000:
            errors.append("🏃 FFLAG_MOTIONING - ĐANG CHUYỂN ĐỘNG")
        if status & 0x10000000:
            errors.append("⏸ FFLAG_MOTIONPAUSE - Motion pause")
        if status & 0x20000000:
            errors.append("⬆️ FFLAG_MOTIONACCEL - Đang tăng tốc")
        if status & 0x40000000:
            errors.append("⬇️ FFLAG_MOTIONDECEL - Đang giảm tốc")
        if status & 0x80000000:
            errors.append("➡️ FFLAG_MOTIONCONST - Tốc độ đều")
        
        if errors:
            print("📋 CÁC CỜ TRẠNG THÁI ĐANG ACTIVE:")
            for err in errors:
                print(f"  {err}")
        else:
            print("✅ Không có cờ nào active (status = 0)")
        
        print("\n" + "=" * 60)
        print("  PHÂN TÍCH")
        print("=" * 60)
        
        # Kiểm tra lỗi nghiêm trọng
        if status & 0x00004000:
            print("\n⚡ LỖI NGUỒN ĐỘNG CƠ PHÁT HIỆN!")
            print("   Nguyên nhân có thể:")
            print("   1. Nguồn 24V chưa được cắm vào driver")
            print("   2. Điện áp nguồn quá thấp (< 20V)")
            print("   3. Fuse nguồn bị đứt")
            print("   4. Cable nguồn bị hở")
            print("\n   ✅ GIẢI PHÁP:")
            print("   - Kiểm tra đèn LED trên driver có sáng không")
            print("   - Đo điện áp giữa +24V và GND")
            print("   - Đảm bảo nguồn 24V DC, 3A")
        
        if status & 0x00000001:
            print("\n❌ CÓ LỖI CHUNG (ERROR_ALL)")
            print("   Cần kiểm tra phần cứng và reset alarm")
        
        if status & 0x00400000:
            print("\n⏸ Motor đang ở trạng thái PT_STOPPED")
            print("   (Đây là trạng thái bình thường khi motor dừng)")
        
        if status & 0x08000000:
            print("\n🏃 Motor ĐANG CHUYỂN ĐỘNG!")
        
    else:
        print("\n❌ Không đọc được trạng thái!")
    
    driver.disconnect()
    print("\n✅ Đã ngắt kết nối")
else:
    print("\n❌ Không thể kết nối motor!")

print("\n" + "=" * 60)
