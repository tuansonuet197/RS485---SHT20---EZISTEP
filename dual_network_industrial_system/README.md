# BÀI TẬP LỚN: HỆ THỐNG GIÁM SÁT VÀ ĐIỀU KHIỂN CÔNG NGHIỆP

**Môn học:** Kiến trúc máy tính và mạng truyền thông công nghiệp  
**Lớp học phần:** INT 2013 44  
**Giảng viên hướng dẫn:**
- ThS. Đặng Anh Việt
- ThS. Nguyễn Quang Nhã

**Sinh viên thực hiện:**
- Họ và tên: Nguyễn Tuấn Sơn
- Mã sinh viên: 23021335

---

## Mô tả đề tài
Xây dựng hệ thống giám sát môi trường và điều khiển động cơ sử dụng 2 mạng RS-485 độc lập với **tính năng tự động hóa thông minh**:
- **Mạng 1 (Modbus RTU)**: Cảm biến nhiệt độ - độ ẩm SHT20 @ 9600 bps
- **Mạng 2 (FASTECH Protocol)**: Driver động cơ bước Ezi-STEP Plus-R @ 115200 bps
- **🤖 Automation**: Điều khiển động cơ tự động dựa trên nhiệt độ/độ ẩm

## Mục tiêu học tập
1. Nắm vững giao thức truyền thông RS-485 trong công nghiệp
2. Hiểu và triển khai Modbus RTU và FASTECH Protocol
3. Xây dựng hệ thống đa nhiệm (multi-threading) với Python
4. Lập trình giao diện người dùng với PyQt5
5. Xử lý dữ liệu thời gian thực và logging

## Cấu trúc dự án
```
dual_network_industrial_system/
├── config/
│   ├── __init__.py
│   └── settings.py          # Cấu hình hệ thống
├── drivers/
│   ├── __init__.py
│   ├── sht20_modbus.py      # Driver SHT20 Modbus RTU
│   └── ezistep_fastech.py   # Driver Ezi-STEP FASTECH
├── gui/
│   ├── __init__.py
│   ├── main_window.py       # Cửa sổ chính với 3 tabs
│   ├── sht20_tab.py         # Tab giám sát SHT20
│   ├── ezistep_tab.py       # Tab điều khiển Ezi-STEP
│   └── automation_tab.py    # 🤖 Tab điều khiển tự động
├── logic/
│   ├── __init__.py
│   └── automation_simple.py # Logic automation rules
├── utils/
│   ├── __init__.py
│   └── logger.py            # Hệ thống ghi log
├── logs/                     # Thư mục chứa log files
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── README.md
```

## Cài đặt

### 1. Cài đặt Python packages
```bash
pip install -r requirements.txt
```

### 2. Cấu hình phần cứng

#### SHT20 (COM1):
- Cổng: COM1
- Baudrate: 9600 bps
- Slave ID: 1
- Dây: A+ (Vàng), B- (Trắng)

#### Ezi-STEP Plus-R (COM2):
- Cổng: COM2
- Baudrate: 115200 bps
- Slave ID: 2
- Kết nối: RJ45 (Chân 3=A, Chân 6=B)
- SW1: Đặt về số 2
- SW2: DIP switches (ON-OFF-OFF-ON)

### 3. Nguồn điện
- 24V DC, tối thiểu 3A
- Đảm bảo GND chung cho cả 2 mạng

## Sử dụng

### Khởi chạy ứng dụng
```bash
python main.py
```

### Giao diện GUI
1. **Tab 1 - Mạng 1 (SHT20)**: 
   - Kết nối/Ngắt kết nối
   - Hiển thị nhiệt độ, độ ẩm realtime
   - Đồ thị theo thời gian
   
2. **Tab 2 - Mạng 2 (Ezi-STEP)**:
   - Kết nối/Ngắt kết nối
   - Điều khiển Jog (Tốc độ, Hướng)
   - Về gốc (Homing)
   - Di chuyển tuyệt đối/tương đối
   - Hiển thị trạng thái động cơ

3. **Tab 3 - 🤖 Điều Khiển Tự Động** (MỚI):
   - Bật/Tắt automation
   - Cấu hình 4 rules tự động:
     * **Rule 1**: Temp > 28°C → Motor CW 8000pps (làm mát)
     * **Rule 2**: Temp < 26°C → Motor STOP (tiết kiệm năng lượng)
     * **Rule 3**: Humidity > 65% → Motor STOP (tắt phun sương)
     * **Rule 4**: Humidity < 40% → Motor CW 5000pps (bật phun sương)
   - Hiển thị trạng thái real-time (temp, humid, motor)
   - Đồ thị nhiệt độ + motor status
   - Activity log ghi lại các sự kiện automation
   - Thống kê số lần trigger

## Tính năng

### Tính năng cơ bản
- ✅ Giao tiếp song song 2 mạng RS-485 độc lập
- ✅ Modbus RTU protocol cho SHT20
- ✅ FASTECH Protocol (với byte stuffing) cho Ezi-STEP
- ✅ Multi-threading với PyQt5
- ✅ Real-time data visualization
- ✅ CSV data logging

### ⭐ Tính năng Automation (MỚI)
- 🤖 **Điều khiển tự động thông minh**: Động cơ tự động bật/tắt dựa trên nhiệt độ/độ ẩm
- 📋 **4 Rules có thể cấu hình**:
  - Rule dựa trên nhiệt độ (High/Low temperature control)
  - Rule dựa trên độ ẩm (High/Low humidity control)
- 🎛️ **Tùy chỉnh ngưỡng**: Thay đổi temp/humid threshold qua GUI
- 📊 **Real-time monitoring**: Đồ thị kết hợp nhiệt độ + motor status
- 📝 **Activity logging**: Ghi lại mọi sự kiện automation
- 📈 **Statistics**: Thống kê số lần trigger cho từng rule

### Ứng dụng thực tế
- 🌡️ **Nhà kính thông minh**: Tự động điều chỉnh thông gió khi nhiệt độ cao
- 💧 **Kiểm soát độ ẩm**: Tự động bật/tắt máy phun sương
- 🏭 **Làm mát thiết bị**: Quạt tự động bật khi nhiệt độ vượt ngưỡng
- 📦 **Kho bảo quản**: Duy trì môi trường ổn định tự động
- ✅ GUI hiện đại với PyQt5
- ✅ Ghi log dữ liệu CSV
- ✅ Xử lý lỗi và reconnect tự động

## Yêu cầu hệ thống
- Windows 10/11
- Python 3.8+
- 2 cổng COM (USB-RS485)
- Nguồn 24V DC

## Demo Automation - Kịch bản test

### Chuẩn bị
1. Khởi động ứng dụng: `python main.py`
2. Kết nối cả 2 mạng (SHT20 + Ezi-STEP)
3. Chuyển sang Tab 3 "Điều Khiển Tự Động"
4. Tick ☑️ "Enable Automation"

### Kịch bản demo cho giảng viên
```
[BƯỚC 1] Hệ thống ở trạng thái bình thường
         - Nhiệt độ: 25.5°C (< 28°C)
         - Motor: STOPPED
         - Status: "🟢 Normal"

[BƯỚC 2] Tay ấm cảm biến SHT20 (hoặc dùng nguồn nhiệt)
         - GUI Tab 1: Nhiệt độ tăng 26... 27... 28... 29°C
         - GUI Tab 3: Temp status → "🔴 HIGH"

[BƯỚC 3] Ngay khi Temp = 28.1°C (vượt ngưỡng Rule 1)
         ✨ AUTOMATION TRIGGER!
         - Motor tự động bật: CW 8000pps
         - Motor status: "🔄 RUNNING (AUTO)"
         - Activity Log: "[HH:MM:SS] ✅ Rule 1: Temp 28.1°C → Motor started CW at 8000pps"
         - Đồ thị: Vùng xanh xuất hiện (motor running)

[BƯỚC 4] Thả tay, nhiệt độ giảm dần 27... 26... 25°C
         - GUI Tab 1: Nhiệt độ giảm
         - GUI Tab 3: Temp status → "🟢 Normal"

[BƯỚC 5] Ngay khi Temp = 25.9°C (dưới ngưỡng Rule 2)
         ✨ AUTOMATION TRIGGER!
         - Motor tự động tắt
         - Motor status: "🛑 STOPPED"
         - Activity Log: "[HH:MM:SS] ✅ Rule 2: Temp 25.9°C → Motor stopped"
         - Đồ thị: Vùng xanh biến mất

[KẾT QUẢ]
✅ Giảng viên thấy rõ sự liên kết giữa 2 mạng:
   - Mạng 1 đọc nhiệt độ → Logic automation xử lý → Mạng 2 điều khiển motor
✅ Hệ thống tự động hóa hoàn toàn (không cần can thiệp tay)
✅ Demo trong 2-3 phút, trực quan, ấn tượng!
```

## Phân bố công việc
- **Phần 1 - Driver RS-485 & Modbus RTU**: Triển khai driver SHT20, xử lý CRC, parsing data
- **Phần 2 - Driver FASTECH Protocol**: Triển khai driver Ezi-STEP, byte stuffing/destuffing, điều khiển động cơ
- **Phần 3 - Giao diện GUI**: PyQt5, threading, real-time plotting
- **Phần 4 - Logic Automation**: Rules engine, signal/slot, automation controller
- **Phần 5 - Tích hợp & kiểm thử**: Kết nối phần cứng, debugging, tối ưu hóa

## Tài liệu tham khảo
- Modbus Protocol Specification v1.1b3
- FASTECH Ezi-STEP Plus-R Communication Manual
- RS-485 Standard (TIA/EIA-485-A)
- PyQt5 Documentation
- Python Serial Communication (pyserial)

## Phiên bản
- **v1.0** (Tháng 11/2025): Phiên bản cơ bản với 2 mạng độc lập
- **v1.1** (Tháng 11/2025): Thêm tính năng Automation - Điều khiển tự động thông minh ⭐

## Video Demo
*(Sẽ cập nhật link video demo khi hoàn thành)*

## Screenshots
*(Sẽ thêm ảnh chụp màn hình GUI khi demo)*

---
**Lưu ý:** Đây là bài tập lớn môn học, không dùng cho mục đích thương mại.
