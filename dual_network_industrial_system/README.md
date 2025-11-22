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
Xây dựng hệ thống giám sát môi trường và điều khiển động cơ sử dụng 2 mạng RS-485 độc lập:
- **Mạng 1 (Modbus RTU)**: Cảm biến nhiệt độ - độ ẩm SHT20 @ 9600 bps
- **Mạng 2 (FASTECH Protocol)**: Driver động cơ bước Ezi-STEP Plus-R @ 115200 bps

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
│   ├── main_window.py       # Cửa sổ chính với 2 tabs
│   ├── sht20_tab.py         # Tab giám sát SHT20
│   └── ezistep_tab.py       # Tab điều khiển Ezi-STEP
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
1. **Tab SHT20**: 
   - Kết nối/Ngắt kết nối
   - Hiển thị nhiệt độ, độ ẩm realtime
   - Đồ thị theo thời gian
   
2. **Tab Ezi-STEP**:
   - Kết nối/Ngắt kết nối
   - Điều khiển Jog (Tốc độ, Hướng)
   - Về gốc (Homing)
   - Di chuyển tuyệt đối/tương đối
   - Hiển thị trạng thái động cơ

## Tính năng
- ✅ Giao tiếp song song 2 mạng độc lập
- ✅ Modbus RTU cho SHT20
- ✅ FASTECH Protocol cho Ezi-STEP
- ✅ GUI hiện đại với PyQt5
- ✅ Ghi log dữ liệu CSV
- ✅ Xử lý lỗi và reconnect tự động

## Yêu cầu hệ thống
- Windows 10/11
- Python 3.8+
- 2 cổng COM (USB-RS485)
- Nguồn 24V DC

## Phân bố công việc
- **Phần 1 - Driver RS-485 & Modbus RTU**: Triển khai driver SHT20, xử lý CRC, parsing data
- **Phần 2 - Driver FASTECH Protocol**: Triển khai driver Ezi-STEP, byte stuffing/destuffing, điều khiển động cơ
- **Phản 3 - Giao diện GUI**: PyQt5, threading, real-time plotting
- **Phần 4 - Tích hợp & kiểm thử**: Kết nối phần cứng, debugging, tối ưu hóa

## Tài liệu tham khảo
- Modbus Protocol Specification v1.1b3
- FASTECH Ezi-STEP Plus-R Communication Manual
- RS-485 Standard (TIA/EIA-485-A)
- PyQt5 Documentation
- Python Serial Communication (pyserial)

## Phiên bản
v1.0 - Tháng 11/2025

---
**Lưu ý:** Đây là bài tập lớn môn học, không dùng cho mục đích thương mại.
