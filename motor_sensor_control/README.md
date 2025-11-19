# Hệ Thống Điều Khiển Motor & Cảm Biến

Dự án điều khiển động cơ bước **Ezi-STEP Plus-R** dựa trên dữ liệu từ cảm biến **SHT20 RS485**.

## 🚀 Cài đặt

### 1. Tạo virtual environment
```bash
python -m venv venv
```

### 2. Kích hoạt virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate UI code
```bash
pyuic5 gui/mainwindow.ui -o gui/ui_mainwindow.py
```

### 5. Chạy ứng dụng
```bash
python main.py
```

## 📖 Cấu hình

Chỉnh sửa file `config.py` để thay đổi:
- Cổng COM
- Slave ID của thiết bị
- Các ngưỡng tự động
- Tốc độ motor

## 🛠️ Test thiết bị

```bash
# Test SHT20
python test_devices.py sht20

# Test Motor
python test_devices.py motor
```

## 📞 Hỗ trợ

Email: support@example.com
