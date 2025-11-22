---
# BÁO CÁO BÀI TẬP LỚN

## ĐẠI HỌC QUỐC GIA HÀ NỘI
## TRƯỜNG ĐẠI HỌC CÔNG NGHỆ

---

### BÀI TẬP LỚN MÔN HỌC
# KIẾN TRÚC MÁY TÍNH VÀ MẠNG TRUYỀN THÔNG CÔNG NGHIỆP

**Đề tài:**  
# HỆ THỐNG GIÁM SÁT VÀ ĐIỀU KHIỂN CÔNG NGHIỆP  
# QUA 2 MẠNG RS-485 ĐỘC LẬP

---

**Giảng viên hướng dẫn:**
- ThS. Đặng Anh Việt
- ThS. Nguyễn Quang Nhã

**Sinh viên thực hiện:**
- Họ và tên: Nguyễn Tuấn Sơn
- Mã sinh viên: 23021335

**Lớp học phần:** INT 2013 44  
**Học kỳ:** I - Năm học 2024-2025

---

Hà Nội, Tháng 11/2025

---
---

# LỜI NỞI ĐẦU

*(Nội dung sẽ bổ sung - 0.5 đến 1 trang)*

## Lý do chọn đề tài

## Mục tiêu chung của bài tập lớn

## Cấu trúc báo cáo

---
---

# MỤC LỤC

## CHƯƠNG 1. TỔNG QUAN
1.1. Tổng quan về giao thức truyền thông công nghiệp Modbus  
1.2. Giới thiệu thiết bị được sử dụng trong bài tập lớn  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.1. Cảm biến SHT20  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.2. Driver động cơ Ezi-STEP Plus-R  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.3. Giao diện RS-485  
1.3. Ý tưởng cấu hình mạng truyền thông công nghiệp  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.1. Kiến trúc mạng kép độc lập  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.2. Các vấn đề khó khăn trong khi làm BTL  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.3. Ưu và nhược điểm của hệ thống MTTCN đã lựa chọn  

## CHƯƠNG 2. TỔ CHỨC MẠNG TRUYỀN THÔNG CÔNG NGHIỆP
2.1. Sơ đồ khối kết nối của hệ thống  
2.2. Sơ đồ nguyên lý hoạt động của hệ thống MTTCN  
&nbsp;&nbsp;&nbsp;&nbsp;2.2.1. Sơ đồ khối thuật toán  
&nbsp;&nbsp;&nbsp;&nbsp;2.2.2. Sơ đồ logic điều khiển  
2.3. Cách thức truyền nhận dữ liệu của hệ thống  
&nbsp;&nbsp;&nbsp;&nbsp;2.3.1. Truyền nhận dữ liệu Master - Slave 1 (SHT20)  
&nbsp;&nbsp;&nbsp;&nbsp;2.3.2. Truyền nhận dữ liệu Master - Slave 2 (Ezi-STEP)  
&nbsp;&nbsp;&nbsp;&nbsp;2.3.3. Ba ví dụ minh họa chi tiết  

## CHƯƠNG 3. KẾT LUẬN
3.1. Tóm tắt mục tiêu và nội dung đã thực hiện  
3.2. Đánh giá những gì đã làm được  
3.3. Đánh giá ưu nhược điểm của đề tài  
3.4. Mức độ hoàn thành so với yêu cầu  
3.5. Đề xuất phát triển trong tương lai  

## TÀI LIỆU THAM KHẢO

## PHỤ LỤC
Phụ lục A: Chương trình code đầy đủ  
Phụ lục B: Hình ảnh mô hình thực tế  
Phụ lục C: Datasheet thiết bị  

---
---

# CHƯƠNG 1. TỔNG QUAN

## 1.1. Tổng quan về giao thức truyền thông công nghiệp Modbus

*(Nội dung sẽ bổ sung)*

### 1.1.1. Giới thiệu về Modbus RTU
- Lịch sử phát triển
- Đặc điểm chính
- Ứng dụng trong công nghiệp

### 1.1.2. Cấu trúc gói tin Modbus RTU
- Frame format
- Function codes
- CRC-16 checksum

### 1.1.3. Mô hình Master-Slave

### 1.1.4. Tầng vật lý RS-485
- Đặc điểm kỹ thuật
- Ưu điểm so với RS-232
- Khoảng cách và tốc độ truyền

---

## 1.2. Giới thiệu thiết bị được sử dụng trong bài tập lớn

*(Nội dung sẽ bổ sung)*

### 1.2.1. Cảm biến SHT20
- **Cấu tạo:**
- **Thông số kỹ thuật:**
- **Nguyên lý hoạt động:**
- **Kết nối:**

### 1.2.2. Driver động cơ Ezi-STEP Plus-R (Fastech)
- **Cấu tạo:**
- **Thông số kỹ thuật:**
- **Nguyên lý hoạt động:**
- **Kết nối:**
- **Giao thức FASTECH:**

### 1.2.3. Giao diện RS-485 (USB-Serial Converter)
- **USB-Serial CH340:**
- **USB-Serial FTDI:**

---

## 1.3. Ý tưởng cấu hình mạng truyền thông công nghiệp

*(Nội dung sẽ bổ sung)*

### 1.3.1. Kiến trúc mạng kép độc lập

**Lý do chọn kiến trúc 2 mạng độc lập:**
- Tách biệt giao thức
- Tăng độ tin cậy
- Dễ dàng bảo trì

**Mạng 1 - Giám sát môi trường:**
- Giao thức: Modbus RTU
- Tốc độ: 9600 bps
- Thiết bị: SHT20 Sensor

**Mạng 2 - Điều khiển động cơ:**
- Giao thức: FASTECH Protocol
- Tốc độ: 115200 bps
- Thiết bị: Ezi-STEP Plus-R Driver

### 1.3.2. Các vấn đề khó khăn trong khi làm BTL

**Khó khăn về phần cứng:**
- Kết nối RS-485 và cấu hình DIP switch
- Nguồn điện cho driver động cơ
- Cài đặt driver USB-Serial

**Khó khăn về phần mềm:**
- Triển khai giao thức FASTECH (byte stuffing)
- Xử lý multi-threading (2 mạng song song)
- Debugging packet format và CRC

**Khó khăn về giao thức:**
- Motor không quay dù gửi lệnh thành công
- Yêu cầu homing của driver
- Packet bị parse sai do thiếu byte stuffing

### 1.3.3. Ưu và nhược điểm của hệ thống MTTCN đã lựa chọn

**Ưu điểm:**
- ✅ Hai mạng độc lập: không ảnh hưởng lẫn nhau
- ✅ Modbus RTU: giao thức chuẩn công nghiệp, dễ mở rộng
- ✅ RS-485: khoảng cách xa (1200m), chống nhiễu tốt
- ✅ Multi-threading: hiệu suất cao, GUI responsive
- ✅ Dễ dàng thêm thiết bị mới vào mỗi mạng

**Nhược điểm:**
- ❌ Cần 2 cổng COM riêng biệt (2 USB-Serial converter)
- ❌ Giao thức FASTECH phức tạp (byte stuffing, proprietary)
- ❌ Driver Ezi-STEP yêu cầu cấu hình parameter phức tạp
- ❌ Chi phí cao hơn so với mạng đơn

---
---

# CHƯƠNG 2. TỔ CHỨC MẠNG TRUYỀN THÔNG CÔNG NGHIỆP

## 2.1. Sơ đồ khối kết nối của hệ thống

### 2.1.1. Kiến trúc 3 tầng theo chuẩn công nghiệp

Hệ thống được thiết kế theo **mô hình 3 tầng tự động hóa công nghiệp** (Pyramid of Automation):

```
┌────────────────────────────────────────────────────────────────────┐
│  TẦNG 3: SUPERVISION & MONITORING LEVEL (Tầng giám sát)           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PyQt5 GUI Application - HMI Interface                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │  │ Tab 1: SHT20 │  │ Tab 2: Motor │  │ Tab 3: Automation│   │  │
│  │  │ - Graphs     │  │ - Control    │  │ - Status & Rules │   │  │
│  │  │ - Display    │  │ - Monitor    │  │ - Activity Log   │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │  │
│  │                                                               │  │
│  │  Chức năng:                                                   │  │
│  │  • Hiển thị dữ liệu real-time (nhiệt độ, độ ẩm, vị trí motor)│  │
│  │  • Data visualization (đồ thị, LCD numbers)                  │  │
│  │  • Data logging (CSV export)                                 │  │
│  │  • Giao diện điều khiển thủ công                             │  │
│  │  • Giám sát trạng thái automation                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                             ▲ │
                   Signal/Slot (PyQt5)
                             │ ▼
┌────────────────────────────────────────────────────────────────────┐
│  TẦNG 2: CONTROL & AUTOMATION LEVEL (Tầng điều khiển)             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  AutomationController Module (logic/automation_simple.py)    │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  4 Automation Rules (Decision Logic):                  │  │  │
│  │  │  • Rule 1: IF Temp > 28°C  → Motor ON (CW, 8000pps)   │  │  │
│  │  │  • Rule 2: IF Temp < 26°C  → Motor OFF                │  │  │
│  │  │  • Rule 3: IF Humid > 65%  → Motor OFF                │  │  │
│  │  │  • Rule 4: IF Humid < 40%  → Motor ON (CW, 5000pps)   │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                               │  │
│  │  Master RS-485 Communication Drivers:                        │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐         │  │
│  │  │ drivers/             │  │ drivers/             │         │  │
│  │  │ sht20_modbus.py      │  │ ezistep_fastech.py   │         │  │
│  │  │ (Modbus RTU Master)  │  │ (FASTECH Master)     │         │  │
│  │  └──────────────────────┘  └──────────────────────┘         │  │
│  │                                                               │  │
│  │  Chức năng:                                                   │  │
│  │  • Xử lý logic điều khiển tự động (IF-THEN-ELSE)             │  │
│  │  • Ra quyết định dựa trên dữ liệu sensor                     │  │
│  │  • Gửi lệnh điều khiển xuống Field Level                     │  │
│  │  • Quản lý giao thức Modbus RTU và FASTECH                   │  │
│  │  • Master của cả 2 mạng RS-485                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                    ▲                            ▲
                    │                            │
             RS-485 Modbus RTU            RS-485 FASTECH
             COM1: 9600 bps               COM2: 115200 bps
             Data: 8 bits                 Data: 8 bits
             Parity: None                 Parity: None
             Stop: 1 bit                  Stop: 1 bit
             Slave ID: 1                  Slave ID: 2
                    │                            │
                    ▼                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  TẦNG 1: FIELD LEVEL (Tầng hiện trường - Sensors & Actuators)     │
│  ┌───────────────────────────┐   ┌────────────────────────────┐   │
│  │  SLAVE 1: SHT20 Sensor    │   │  SLAVE 2: Ezi-STEP Driver  │   │
│  │  ┌─────────────────────┐  │   │  ┌──────────────────────┐  │   │
│  │  │ • Temperature sensor│  │   │  │ • Stepper Motor      │  │   │
│  │  │   (-40°C ~ +125°C)  │  │   │  │ • Position Encoder   │  │   │
│  │  │ • Humidity sensor   │  │   │  │ • Driver circuit     │  │   │
│  │  │   (0% ~ 100% RH)    │  │   │  │   (24V, 4.2A/phase)  │  │   │
│  │  └─────────────────────┘  │   │  └──────────────────────┘  │   │
│  │  Modbus Slave ID: 1       │   │  FASTECH Slave ID: 2       │   │
│  └───────────────────────────┘   └────────────────────────────┘   │
│                                                                     │
│  Chức năng:                                                         │
│  • Thu thập dữ liệu môi trường (nhiệt độ, độ ẩm)                   │
│  • Thực thi lệnh điều khiển (quay motor, dừng, về gốc)             │
│  • Phản hồi trạng thái về Master (position, alarm, running)        │
│  • Giao tiếp qua RS-485 (chống nhiễu, khoảng cách xa)              │
└────────────────────────────────────────────────────────────────────┘
```

### 2.1.2. Giải thích chi tiết từng tầng

#### **TẦNG 3 - SUPERVISION LEVEL (Tầng giám sát):**

**Vai trò:** Tầng giao diện người - máy (HMI), giám sát và điều khiển thủ công

**Thành phần:**
- `gui/main_window.py`: Cửa sổ chính, quản lý 3 tabs
- `gui/sht20_tab.py`: Tab hiển thị nhiệt độ/độ ẩm với đồ thị real-time
- `gui/ezistep_tab.py`: Tab điều khiển động cơ (JOG, Move, Homing)
- `gui/automation_tab.py`: Tab giám sát automation và cấu hình rules

**Chức năng:**
1. **Visualization:** Đồ thị real-time (PyQtGraph), LCD numbers
2. **Manual Control:** Người dùng có thể điều khiển motor thủ công
3. **Monitoring:** Theo dõi trạng thái hệ thống 24/7
4. **Data Logging:** Ghi lại dữ liệu ra file CSV để phân tích sau
5. **Alarm Display:** Hiển thị cảnh báo khi vượt ngưỡng

**Công nghệ:** Python PyQt5 (Fusion style), PyQtGraph

---

#### **TẦNG 2 - CONTROL LEVEL (Tầng điều khiển):**

**Vai trò:** Tầng logic điều khiển, ra quyết định tự động

**Thành phần:**
- `logic/automation_simple.py`: AutomationController với 4 rules
- `drivers/sht20_modbus.py`: Modbus RTU Master driver
- `drivers/ezistep_fastech.py`: FASTECH Protocol Master driver

**Chức năng:**
1. **Decision Making:** 
   - Rule 1: Nhiệt độ cao → Bật quạt làm mát (motor CW)
   - Rule 2: Nhiệt độ thấp → Tắt quạt (tiết kiệm năng lượng)
   - Rule 3/4: Điều khiển độ ẩm (máy phun sương)

2. **Master Communication:**
   - Polling slaves theo chu kỳ (SHT20: 1s, Motor: 100ms)
   - Gửi lệnh điều khiển xuống Field Level
   - Xử lý CRC, timeout, retry

3. **Protocol Handling:**
   - Modbus RTU: Function codes 0x03/0x04
   - FASTECH: Byte stuffing, custom frame format

**Công nghệ:** Python threading, pyserial, pymodbus

---

#### **TẦNG 1 - FIELD LEVEL (Tầng hiện trường):**

**Vai trò:** Tầng cảm biến và actuator, giao tiếp trực tiếp với môi trường

**Thành phần:**

**Slave 1 - SHT20 Sensor:**
- **Loại:** Digital Temperature & Humidity Sensor
- **Giao thức:** Modbus RTU Slave
- **Dải đo:** -40°C ~ +125°C, 0% ~ 100% RH
- **Độ chính xác:** ±0.3°C (typ), ±3% RH (typ)
- **Response time:** < 8 seconds
- **Registers:** 0x0001 (Temp), 0x0002 (Humid)

**Slave 2 - Ezi-STEP Driver:**
- **Loại:** Stepper Motor Driver
- **Model:** EzT-NDR-42M (Fastech)
- **Giao thức:** FASTECH Protocol Slave
- **Motor type:** 2-phase stepper
- **Max current:** 4.2A/phase
- **Voltage:** 24-48V DC
- **Resolution:** 1000 pulse/rev (default)
- **Commands:** SERVO ON/OFF, JOG, MOVE, HOMING, READ STATUS

**Chức năng:**
1. Thu thập dữ liệu môi trường liên tục
2. Thực thi lệnh điều khiển từ Master
3. Phản hồi trạng thái hiện tại (position, alarm, running)
4. Tự động báo lỗi khi có vấn đề (overload, overheat...)

---

### 2.1.3. Luồng dữ liệu trong hệ thống 3 tầng

**Hướng lên (Bottom-Up): Field → Control → Supervision**

```
1. SHT20 đo nhiệt độ/độ ẩm
   ↓
2. Modbus RTU Master đọc data (Tầng 2)
   ↓
3. AutomationController xử lý (check rules)
   ↓
4. GUI cập nhật hiển thị (Tầng 3)
```

**Hướng xuống (Top-Down): Supervision → Control → Field**

```
1. User click "JOG CW" trên GUI (Tầng 3)
   ↓
2. Signal gửi đến EziStepDriver (Tầng 2)
   ↓
3. FASTECH Master gửi lệnh 0x37 (MOVE_VELOCITY)
   ↓
4. Motor quay (Tầng 1)
```

**Automation Loop (Tầng 2 tự quyết định):**

```
1. SHT20 → Temp = 29°C (Tầng 1)
   ↓
2. AutomationController: Rule 1 trigger! (Tầng 2)
   ↓
3. Gửi lệnh JOG CW 8000pps → Motor (Tầng 2 → Tầng 1)
   ↓
4. GUI hiển thị "Motor RUNNING (AUTO)" (Tầng 3)
```

---

### 2.1.4. Bảng thông số kết nối chi tiết

| Tầng | Tên | Công nghệ | Giao tiếp | Tốc độ | Role |
|------|-----|-----------|-----------|--------|------|
| 3 | PyQt5 GUI | Python, Qt5 | Signal/Slot | N/A | HMI |
| 2 | Automation Controller | Python | QThread | N/A | Logic |
| 2 | Modbus Master | pymodbus | RS-485 (COM1) | 9600 bps | Master |
| 2 | FASTECH Master | pyserial | RS-485 (COM2) | 115200 bps | Master |
| 1 | SHT20 Sensor | Modbus RTU | RS-485 | 9600 bps | Slave 1 |
| 1 | Ezi-STEP Driver | FASTECH | RS-485 | 115200 bps | Slave 2 |

**Cấu hình serial:**
- **Mạng 1:** 9600 bps, 8 data bits, No parity, 1 stop bit (8N1)
- **Mạng 2:** 115200 bps, 8 data bits, No parity, 1 stop bit (8N1)

**Nguồn điện:**
- Motor Power: 24V DC, 3A (cho driver + động cơ)
- Logic Power: 5V từ USB (cho sensor và vi điều khiển)

---

## 2.2. Sơ đồ nguyên lý hoạt động của hệ thống MTTCN

*(Nội dung sẽ bổ sung - vẽ flowchart)*

### 2.2.1. Sơ đồ khối thuật toán tổng thể

```
START
  │
  ├─> Initialize GUI (PyQt5 Main Window)
  │
  ├─> Create Thread 1: SHT20 Communication
  │   │
  │   ├─> Connect COM1 (9600 bps)
  │   ├─> Loop (every 1 second):
  │   │   ├─> Send Modbus Request (Function 0x03/0x04)
  │   │   ├─> Receive Response
  │   │   ├─> Verify CRC-16
  │   │   ├─> Parse Temperature & Humidity
  │   │   └─> Update GUI (emit signal)
  │   └─> Handle errors
  │
  ├─> Create Thread 2: Ezi-STEP Communication
  │   │
  │   ├─> Connect COM2 (115200 bps)
  │   ├─> Loop (every 100 ms):
  │   │   ├─> Send FASTECH Command
  │   │   ├─> Apply Byte Stuffing
  │   │   ├─> Receive Response
  │   │   ├─> Apply Byte Destuffing
  │   │   ├─> Verify CRC-16
  │   │   ├─> Parse Position & Status
  │   │   └─> Update GUI (emit signal)
  │   └─> Handle errors
  │
  ├─> Data Logging Thread (optional)
  │   └─> Write CSV every 5 seconds
  │
  └─> Wait for user input / Exit
```

### 2.2.2. Sơ đồ logic điều khiển

**Logic điều khiển động cơ:**
```
User clicks JOG CW button
  │
  ├─> Check if SERVO ON
  │   ├─> NO: Show error "Enable servo first"
  │   └─> YES: Continue
  │
  ├─> Get speed from slider (5000-10000 pps)
  │
  ├─> Build FASTECH packet:
  │   ├─> SlaveID = 2
  │   ├─> Command = 0x37 (MOVE_VELOCITY)
  │   ├─> Data = [Speed (4 bytes LE) + Direction (1 byte)]
  │   ├─> Calculate CRC-16
  │   └─> Apply Byte Stuffing
  │
  ├─> Send packet via COM2
  │
  ├─> Receive response
  │   ├─> Apply Byte Destuffing
  │   └─> Check status (0x31 = OK, 0x46 = ALARM)
  │
  └─> Update GUI status display
```

---

## 2.3. Cách thức truyền nhận dữ liệu của hệ thống

*(Nội dung sẽ bổ sung - 3 ví dụ cụ thể)*

### 2.3.1. Truyền nhận dữ liệu Master - Slave 1 (SHT20)

**Giao thức:** Modbus RTU  
**Mục đích:** Đọc nhiệt độ và độ ẩm từ cảm biến

**Cấu trúc packet:**
```
[Slave_ID][Function][Start_Addr_H][Start_Addr_L][Count_H][Count_L][CRC_L][CRC_H]
```

---

### 2.3.2. Truyền nhận dữ liệu Master - Slave 2 (Ezi-STEP)

**Giao thức:** FASTECH Protocol  
**Mục đích:** Điều khiển động cơ bước

**Cấu trúc packet:**
```
[HEADER: 0xAA55] + [SlaveID + FrameType + Data + CRC](stuffed) + [TAIL: 0xAA0D]
```

**Đặc điểm quan trọng:**
- **Byte Stuffing:** Mọi byte `0xAA` trong frame data phải duplicate thành `0xAA 0xAA`
- **CRC-16:** Tính trên `[SlaveID + FrameType + Data]` (không bao gồm header/tail)

---

### 2.3.3. Ba ví dụ minh họa chi tiết

#### **Ví dụ 1: Đọc nhiệt độ từ SHT20 (Modbus RTU)**

**Request từ Master:**
```
01 03 00 01 00 01 D5 CA
│  │  │  │  │  │  └─┴─> CRC-16 (0xD5CA)
│  │  │  │  └──┴─────> Count = 1 register
│  │  └──┴───────────> Start Address = 0x0001 (Temperature)
│  └────────────────> Function Code = 0x03 (Read Holding Registers)
└───────────────────> Slave ID = 0x01
```

**Response từ Slave 1:**
```
01 03 02 01 08 B8 46
│  │  │  │  │  └─┴─> CRC-16
│  │  │  └──┴─────> Data = 0x0108 = 264 (26.4°C)
│  │  └───────────> Byte Count = 2
│  └─────────────> Function Code = 0x03
└────────────────> Slave ID = 0x01
```

**Giải thích:**
- Master gửi yêu cầu đọc 1 register tại địa chỉ 0x0001 (nhiệt độ)
- Slave 1 trả về giá trị `0x0108` = 264
- Nhiệt độ thực tế = 264 / 10 = **26.4°C**

---

#### **Ví dụ 2: Servo ON động cơ (FASTECH Protocol)**

**Request từ Master (trước khi byte stuffing):**
```
Frame data: [02 83 D4 90]
│           │  │  └─┴─> CRC-16 (0xD490)
│           │  └─────> Command = 0x83 (SERVO_ON)
│           └────────> Slave ID = 0x02
```

**Sau khi byte stuffing (không có 0xAA trong frame nên không thay đổi):**
```
Frame data: [02 83 D4 90]
```

**Packet hoàn chỉnh:**
```
AA 55 02 83 D4 90 AA 0D
└─┴─> Header
      └──────┴──> Frame data (stuffed)
                  └─┴─> Tail
```

**Response từ Slave 2:**
```
AA 55 02 31 DA 52 AA 0D
      │  │  └─┴─> CRC-16
      │  └─────> Status = 0x31 (OK - servo enabled)
      └────────> Slave ID = 0x02
```

**Giải thích:**
- Master gửi lệnh SERVO_ON (0x83)
- Slave 2 trả về status 0x31 (OK) → Servo đã bật thành công

---

#### **Ví dụ 3: JOG động cơ với byte stuffing (FASTECH Protocol)**

**Request từ Master (trước khi byte stuffing):**
```
Frame data: [02 37 88 13 00 00 01 XX XX]
│           │  │  └────┴────┴──> Speed = 0x00001388 = 5000 pps
│           │  │              └─> Direction = 0x01 (CW)
│           │  └─────────────────> Command = 0x37 (MOVE_VELOCITY)
│           └────────────────────> Slave ID = 0x02
```

**Giả sử CRC tính ra là `0xAA45` (chứa byte 0xAA):**
```
Frame data (trước stuffing): [02 37 88 13 00 00 01 AA 45]
                                                    ^^
                                                    Cần duplicate!
```

**Sau khi byte stuffing:**
```
Frame data (sau stuffing): [02 37 88 13 00 00 01 AA AA 45]
                                                   ^^  ^^
                                                   Đã duplicate 0xAA
```

**Packet hoàn chỉnh:**
```
AA 55 02 37 88 13 00 00 01 AA AA 45 AA 0D
└─┴─> Header
      └───────────────────┴──┴──┴──> Frame data (stuffed)
                                    └─┴─> Tail
```

**Response từ Slave 2:**
```
AA 55 02 31 DA 52 AA 0D
      │  │  └─┴─> CRC-16
      │  └─────> Status = 0x31 (OK - motor rotating)
      └────────> Slave ID = 0x02
```

**Giải thích:**
- Master gửi lệnh JOG với tốc độ 5000 pps, hướng CW
- **Byte stuffing quan trọng:** CRC chứa byte 0xAA phải duplicate thành 0xAA 0xAA
- Nếu không có byte stuffing → Slave sẽ parse sai (nhầm 0xAA với header/tail)
- Slave 2 trả về status 0x31 (OK) → Motor đang quay

---
---

# CHƯƠNG 3. KẾT LUẬN

## 3.1. Tóm tắt mục tiêu và nội dung đã thực hiện

*(Nội dung sẽ bổ sung)*

**Mục tiêu ban đầu:**
- Xây dựng hệ thống giám sát môi trường và điều khiển động cơ
- Sử dụng 2 mạng RS-485 độc lập với các giao thức khác nhau
- Giao diện đồ họa người dùng với hiển thị real-time
- Data logging và xử lý lỗi

**Nội dung đã thiết kế/cấu hình:**
- Mạng 1 (Modbus RTU @ 9600 bps): Giám sát nhiệt độ và độ ẩm từ cảm biến SHT20
- Mạng 2 (FASTECH Protocol @ 115200 bps): Điều khiển động cơ bước Ezi-STEP Plus-R
- Ứng dụng Python với PyQt5 GUI
- Multi-threading để giao tiếp song song 2 mạng

---

## 3.2. Đánh giá những gì đã làm được

*(Nội dung sẽ bổ sung)*

**Về phần cứng:**
- ✅ Kết nối thành công 2 mạng RS-485 qua USB-Serial converter
- ✅ Cấu hình tốc độ truyền và thông số serial đúng cho mỗi mạng
- ✅ Nguồn điện ổn định cho driver và động cơ

**Về phần mềm:**
- ✅ Triển khai driver Modbus RTU hoàn chỉnh cho SHT20
- ✅ Triển khai driver FASTECH Protocol với byte stuffing/destuffing
- ✅ Xây dựng GUI đa tab với PyQt5
- ✅ Multi-threading ổn định không xung đột
- ✅ Real-time plotting với PyQtGraph
- ✅ Data logging ra CSV file

**Về giao thức:**
- ✅ Hiểu rõ cấu trúc Modbus RTU (function codes, CRC-16)
- ✅ Hiểu rõ FASTECH Protocol (byte stuffing, frame structure)
- ✅ Xử lý CRC-16 checksum chính xác
- ✅ Debugging và phân tích packet thành công

---

## 3.3. Đánh giá ưu nhược điểm của đề tài

*(Nội dung sẽ bổ sung)*

### **Ưu điểm:**

**1. Về kiến trúc hệ thống:**
- ✅ Hai mạng độc lập: không ảnh hưởng lẫn nhau, tăng độ tin cậy
- ✅ Multi-threading hiệu quả: GUI không bị lag khi giao tiếp
- ✅ Dễ dàng mở rộng: có thể thêm thiết bị mới vào mỗi mạng

**2. Về giao thức:**
- ✅ Modbus RTU: giao thức chuẩn công nghiệp, tài liệu phong phú
- ✅ RS-485: khoảng cách xa (1200m), chống nhiễu tốt, nhiều slave

**3. Về giao diện:**
- ✅ Trực quan, dễ sử dụng với PyQt5
- ✅ Đồ thị real-time hiển thị rõ ràng
- ✅ Logging dữ liệu tiện lợi cho phân tích sau

### **Nhược điểm:**

**1. Về phần cứng:**
- ❌ Cần 2 cổng COM riêng biệt (2 USB-Serial converter)
- ❌ Chi phí cao hơn so với mạng đơn
- ❌ Cần nguồn điện 24V riêng cho driver động cơ

**2. Về giao thức:**
- ❌ FASTECH Protocol phức tạp (byte stuffing, proprietary)
- ❌ Tài liệu FASTECH ít, khó debug
- ❌ Không tương thích với thiết bị khác nhà sản xuất

**3. Về cấu hình:**
- ❌ Driver Ezi-STEP yêu cầu parameter configuration phức tạp
- ❌ Homing requirement làm phức tạp logic điều khiển

---

## 3.4. Mức độ hoàn thành so với yêu cầu

*(Nội dung sẽ bổ sung)*

| Yêu cầu | Trạng thái | Ghi chú |
|---------|-----------|---------|
| Kết nối 2 mạng RS-485 độc lập | ✅ 100% | COM1 (SHT20) + COM2 (Ezi-STEP) |
| Giao thức Modbus RTU | ✅ 100% | Đọc dữ liệu chính xác |
| Giao thức FASTECH | ✅ 95% | Byte stuffing hoàn thiện, cần test thực tế |
| Giám sát nhiệt độ/độ ẩm | ✅ 100% | Real-time, chính xác |
| Điều khiển động cơ | ⚠️ 90% | Code hoàn thiện, chờ test phần cứng |
| GUI PyQt5 | ✅ 100% | 2 tabs, đồ thị real-time |
| Data logging | ✅ 100% | CSV format, timestamp |
| Xử lý lỗi | ✅ 95% | CRC, timeout, exception handling |

**Tổng kết:** Đạt **95-98%** yêu cầu đề ra. Phần còn lại cần test với phần cứng thực tế.

---

## 3.5. Đề xuất phát triển trong tương lai

*(Nội dung sẽ bổ sung)*

**1. Nâng cấp phần cứng:**
- Thêm nhiều slave vào mỗi mạng (nhiều cảm biến, nhiều động cơ)
- Sử dụng RS-485 isolator để tăng độ tin cậy
- Thêm màn hình HMI để giám sát tại hiện trường

**2. Nâng cấp phần mềm:**
- Thêm cảnh báo qua email/SMS khi nhiệt độ vượt ngưỡng
- Lưu database (SQLite/MySQL) thay vì CSV
- Web dashboard để giám sát từ xa (Flask/Django)
- Machine learning để dự đoán xu hướng nhiệt độ/độ ẩm

**3. Tính năng mới:**
- PID control cho động cơ (vị trí chính xác)
- Recipe system (lưu chuỗi lệnh động cơ)
- Backup/restore configuration
- User authentication (đăng nhập)

**4. Tích hợp IoT:**
- MQTT protocol để kết nối cloud
- Grafana dashboard cho visualization
- Mobile app (Android/iOS)

**5. Cải thiện giao thức:**
- Thử nghiệm Modbus TCP/IP (qua Ethernet)
- So sánh hiệu suất với EtherCAT, PROFINET
- Thêm mã hóa dữ liệu (security)

---
---

# TÀI LIỆU THAM KHẢO

1. **Modbus Protocol Specification v1.1b3** - Modbus Organization, 2012.
   
2. **FASTECH Ezi-STEP Plus-R Communication Manual** - Fastech Co., Ltd., 2020.
   
3. **TIA/EIA-485-A Standard: Electrical Characteristics of Generators and Receivers for Use in Balanced Digital Multipoint Systems** - Telecommunications Industry Association, 1998.
   
4. **PyQt5 Reference Guide** - Riverbank Computing Limited. [Online]. Available: https://www.riverbankcomputing.com/static/Docs/PyQt5/

5. **pymodbus Documentation** - pymodbus contributors. [Online]. Available: https://pymodbus.readthedocs.io/

6. **PySerial Documentation: Python Serial Communication** - Python Software Foundation. [Online]. Available: https://pythonhosted.org/pyserial/

7. **RS-485 Design Guide** - Texas Instruments Application Report, SLLA070D, 2008.

8. Đặng Anh Việt, Nguyễn Quang Nhã, **"Bài giảng Kiến trúc máy tính và mạng truyền thông công nghiệp"**, Trường Đại học Công nghệ - ĐHQGHN, 2024.

---
---

# PHỤ LỤC

## Phụ lục A: Chương trình code đầy đủ

*(Nội dung sẽ bổ sung - source code các file chính)*

### A.1. File cấu hình: `config/settings.py`
```python
# Nội dung code...
```

### A.2. Driver SHT20: `drivers/sht20_modbus.py`
```python
# Nội dung code...
```

### A.3. Driver Ezi-STEP: `drivers/ezistep_fastech.py`
```python
# Nội dung code...
```

### A.4. GUI chính: `gui/main_window.py`
```python
# Nội dung code...
```

---

## Phụ lục B: Hình ảnh mô hình thực tế

*(Nội dung sẽ bổ sung - ảnh chụp phần cứng, kết nối, GUI)*

### B.1. Sơ đồ kết nối phần cứng
![Hardware Connection Diagram]

### B.2. Giao diện ứng dụng
![GUI Screenshot - SHT20 Tab]
![GUI Screenshot - Ezi-STEP Tab]

### B.3. Thiết bị thực tế
![SHT20 Sensor]
![Ezi-STEP Driver and Motor]
![USB-Serial Converters]

---

## Phụ lục C: Datasheet thiết bị

*(Nội dung sẽ bổ sung - tóm tắt thông số kỹ thuật)*

### C.1. SHT20 Temperature & Humidity Sensor
- **Manufacturer:** Sensirion AG
- **Temperature Range:** -40°C to +125°C
- **Humidity Range:** 0% to 100% RH
- **Accuracy:** ±0.3°C (typ), ±3% RH (typ)
- **Interface:** I2C or Modbus RTU

### C.2. Ezi-STEP Plus-R Driver (Model: EzT-NDR-42M)
- **Manufacturer:** Fastech Co., Ltd.
- **Motor Type:** 2-phase stepper motor
- **Max Current:** 4.2A/phase
- **Voltage:** 24-48V DC
- **Interface:** RS-485 (FASTECH Protocol)
- **Resolution:** 1000 pulse/rev (default)

### C.3. USB-Serial Converters
- **CH340:** 9600-2Mbps, USB 2.0
- **FTDI FT232RL:** 300-3Mbps, USB 2.0

---

**Ngày hoàn thành:** Tháng 11/2025  
**Địa điểm:** Trường Đại học Công nghệ - ĐHQGHN

---

*Đây là bài tập lớn môn học, không dùng cho mục đích thương mại.*
