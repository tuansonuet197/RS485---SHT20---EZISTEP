# Hệ Thống Tự Động Hóa Công Nghiệp - Mạng Kép Độc Lập

## Tổng quan
Hệ thống giám sát môi trường và điều khiển chuyển động với 2 mạng RS485 độc lập:
- **Nhánh 1**: Cảm biến SHT20 (Modbus RTU @ 9600 bps)
- **Nhánh 2**: Driver Ezi-STEP Plus-R (FASTECH Protocol @ 115200 bps)

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

## Tác giả
Phát triển cho Hệ thống Tự động hóa Công nghiệp

## Phiên bản
1.0 - November 2025
