"""
Cấu hình hệ thống - Dual Network Industrial System
"""

# ==================== NHÁNH 1: SHT20 MODBUS RTU ====================
SHT20_CONFIG = {
    'port': 'COM1',              # Cổng COM cho SHT20
    'baudrate': 9600,            # Tốc độ truyền
    'data_bits': 8,
    'stop_bits': 1,
    'parity': 'N',               # None
    'timeout': 1.0,              # Timeout 1 giây
    'slave_id': 1,               # Địa chỉ Modbus
    
    # Địa chỉ thanh ghi Modbus
    'registers': {
        'temperature': 0x0001,   # Nhiệt độ (°C x 10)
        'humidity': 0x0002,      # Độ ẩm (%RH x 10)
        'device_id': 0x0101,     # ID thiết bị
        'baudrate_reg': 0x0102   # Cấu hình baudrate
    },
    
    # Giới hạn đo
    'limits': {
        'temp_min': -40.0,
        'temp_max': 60.0,
        'humidity_min': 0.0,
        'humidity_max': 80.0
    },
    
    # Tần suất đọc dữ liệu (ms)
    'read_interval': 1000
}

# ==================== NHÁNH 2: EZI-STEP FASTECH ====================
EZISTEP_CONFIG = {
    'port': 'COM2',              # Cổng COM cho Ezi-STEP
    'baudrate': 115200,          # Tốc độ truyền cao
    'data_bits': 8,
    'stop_bits': 1,
    'parity': 'N',
    'timeout': 0.5,              # Timeout 500ms (phản hồi nhanh)
    'slave_id': 2,               # Địa chỉ thiết bị (SW1 = 2)
    
    # Thông số động cơ
    'motor': {
        'resolution': 10000,     # 10,000 xung/vòng
        'max_speed': 3000,       # RPM tối đa
        'acceleration': 1000,    # Gia tốc (pps²)
        'deceleration': 1000     # Giảm tốc (pps²)
    },
    
    # Giới hạn hành trình (pulse)
    'limits': {
        'min_position': -100000,
        'max_position': 100000
    },
    
    # FASTECH Protocol
    'protocol': {
        'header': [0xAA, 0xCC],
        'tail': [0xAA, 0xEE]
    },
    
    # Command codes (Mã lệnh chính)
    'commands': {
        'jog_move': 0x37,
        'move_absolute': 0x38,
        'move_relative': 0x39,
        'stop': 0x31,
        'servo_on': 0x83,
        'servo_off': 0x84,
        'homing': 0x23,
        'read_position': 0x0C
    }
}

# ==================== GUI SETTINGS ====================
GUI_CONFIG = {
    'window_title': 'Hệ Thống Tự Động Hóa Công Nghiệp - Mạng Kép',
    'window_size': (1200, 800),
    'refresh_rate': 100,         # ms (cập nhật GUI)
    
    # Màu sắc theme
    'colors': {
        'primary': '#2196F3',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#F44336',
        'background': '#FAFAFA',
        'text': '#212121'
    },
    
    # Đồ thị
    'graph': {
        'max_points': 100,       # Số điểm hiển thị tối đa
        'line_width': 2
    }
}

# ==================== LOGGING SETTINGS ====================
LOG_CONFIG = {
    'enable': True,
    'directory': 'logs',
    'filename_prefix': 'system_log',
    'csv_fields': [
        'timestamp',
        'temperature',
        'humidity',
        'motor_position',
        'motor_status'
    ],
    'log_interval': 5000        # ms (ghi log mỗi 5 giây)
}

# ==================== SYSTEM SETTINGS ====================
SYSTEM_CONFIG = {
    'auto_reconnect': True,
    'reconnect_delay': 3000,    # ms
    'max_reconnect_attempts': 5
}
