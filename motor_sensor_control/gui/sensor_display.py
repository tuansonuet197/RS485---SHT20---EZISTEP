"""
GUI hiển thị nhiệt độ và độ ẩm từ SHT20
Giao diện đẹp mắt với PyQt5
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox, QTextEdit)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

sys.path.append('..')
from devices.rs485_manager import RS485Manager
from devices.sht20_modbus import SHT20Modbus
import config


class SensorDisplayWindow(QMainWindow):
    """Cửa sổ hiển thị cảm biến"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌡️ SHT20 Sensor Monitor")
        self.setGeometry(100, 100, 900, 600)
        
        # RS485 và SHT20
        self.rs485 = None
        self.sht20 = None
        self.is_connected = False
        
        # Dữ liệu hiện tại
        self.current_temp = 0.0
        self.current_humidity = 0.0
        
        # Timer để đọc dữ liệu
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_sensor_data)
        
        self.init_ui()
        self.apply_stylesheet()
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # ===== TIÊU ĐỀ =====
        title_label = QLabel("🌡️ SHT20 TEMPERATURE & HUMIDITY MONITOR")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 20px;")
        main_layout.addWidget(title_label)
        
        # ===== THÔNG TIN KẾT NỐI =====
        info_label = QLabel(f"📡 Port: {config.SHT20_PORT} | Baudrate: {config.SHT20_BAUDRATE} | Slave ID: {config.SHT20_SLAVE_ID}")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        main_layout.addWidget(info_label)
        
        # ===== TRẠNG THÁI KẾT NỐI =====
        self.status_label = QLabel("⚪ Disconnected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 100px;
        """)
        main_layout.addWidget(self.status_label)
        
        # ===== KHUNG HIỂN THỊ DỮ LIỆU =====
        data_layout = QHBoxLayout()
        
        # Khung nhiệt độ
        temp_group = self.create_sensor_group(
            "🌡️ TEMPERATURE", 
            "temp", 
            "°C",
            "#e74c3c"  # Đỏ
        )
        data_layout.addWidget(temp_group)
        
        # Khung độ ẩm
        humidity_group = self.create_sensor_group(
            "💧 HUMIDITY",
            "humidity",
            "%RH",
            "#3498db"  # Xanh dương
        )
        data_layout.addWidget(humidity_group)
        
        main_layout.addLayout(data_layout)
        
        # ===== NÚT ĐIỀU KHIỂN =====
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.setMinimumHeight(50)
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        
        self.start_btn = QPushButton("▶️ Start Reading")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.toggle_reading)
        button_layout.addWidget(self.start_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Log")
        self.clear_btn.setMinimumHeight(50)
        self.clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # ===== LOG AREA =====
        log_label = QLabel("📋 Activity Log:")
        log_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px; margin-top: 10px;")
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            background-color: #ecf0f1;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Courier New';
            font-size: 12px;
        """)
        main_layout.addWidget(self.log_text)
        
        # Log ban đầu
        self.add_log("🚀 Application started")
        self.add_log(f"📡 Waiting to connect to {config.SHT20_PORT}...")
    
    def create_sensor_group(self, title, value_name, unit, color):
        """Tạo khung hiển thị cho một cảm biến"""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {color};
                border: 3px solid {color};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px 20px;
                background-color: white;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Giá trị lớn
        value_label = QLabel("--.-")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"""
            font-size: 72px;
            font-weight: bold;
            color: {color};
            padding: 20px;
        """)
        layout.addWidget(value_label)
        
        # Đơn vị
        unit_label = QLabel(unit)
        unit_label.setAlignment(Qt.AlignCenter)
        unit_label.setStyleSheet(f"""
            font-size: 24px;
            color: {color};
            padding-bottom: 20px;
        """)
        layout.addWidget(unit_label)
        
        group.setLayout(layout)
        
        # Lưu reference để cập nhật sau
        if value_name == "temp":
            self.temp_value_label = value_label
        else:
            self.humidity_value_label = value_label
        
        return group
    
    def apply_stylesheet(self):
        """Áp dụng stylesheet cho toàn bộ window"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
    
    def toggle_connection(self):
        """Bật/tắt kết nối"""
        if not self.is_connected:
            self.connect_sensor()
        else:
            self.disconnect_sensor()
    
    def connect_sensor(self):
        """Kết nối với SHT20"""
        self.add_log(f"🔌 Connecting to {config.SHT20_PORT}...")
        
        try:
            self.rs485 = RS485Manager(config.SHT20_PORT, config.SHT20_BAUDRATE)
            
            if self.rs485.connect():
                self.sht20 = SHT20Modbus(self.rs485, config.SHT20_SLAVE_ID)
                self.is_connected = True
                
                self.status_label.setText("🟢 Connected")
                self.status_label.setStyleSheet("""
                    background-color: #27ae60;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 100px;
                """)
                
                self.connect_btn.setText("🔌 Disconnect")
                self.start_btn.setEnabled(True)
                
                self.add_log("✅ Connected successfully!")
            else:
                self.add_log(f"❌ Failed to connect to {config.SHT20_PORT}")
                self.add_log("⚠️ Check COM port and cable connection")
        
        except Exception as e:
            self.add_log(f"❌ Connection error: {str(e)}")
    
    def disconnect_sensor(self):
        """Ngắt kết nối"""
        if self.read_timer.isActive():
            self.read_timer.stop()
            self.start_btn.setText("▶️ Start Reading")
        
        if self.rs485:
            self.rs485.disconnect()
        
        self.is_connected = False
        self.status_label.setText("⚪ Disconnected")
        self.status_label.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 100px;
        """)
        
        self.connect_btn.setText("🔌 Connect")
        self.start_btn.setEnabled(False)
        
        self.add_log("🔌 Disconnected")
    
    def toggle_reading(self):
        """Bật/tắt đọc dữ liệu"""
        if not self.read_timer.isActive():
            self.read_timer.start(2000)  # Đọc mỗi 2 giây
            self.start_btn.setText("⏹️ Stop Reading")
            self.add_log("▶️ Started continuous reading (2s interval)")
        else:
            self.read_timer.stop()
            self.start_btn.setText("▶️ Start Reading")
            self.add_log("⏹️ Stopped reading")
    
    def read_sensor_data(self):
        """Đọc dữ liệu từ cảm biến"""
        if not self.sht20:
            return
        
        try:
            data = self.sht20.read_temp_humidity()
            
            if data:
                temp, humidity = data
                self.current_temp = temp
                self.current_humidity = humidity
                
                # Cập nhật hiển thị
                self.temp_value_label.setText(f"{temp:.1f}")
                self.humidity_value_label.setText(f"{humidity:.1f}")
                
                # Log
                self.add_log(f"📊 Temp: {temp:.1f}°C | Humidity: {humidity:.1f}%RH")
                
                # Kiểm tra cảnh báo
                if temp > config.AUTO_TEMP_HIGH:
                    self.add_log(f"⚠️ HIGH TEMPERATURE: {temp:.1f}°C")
                elif temp < config.AUTO_TEMP_LOW:
                    self.add_log(f"⚠️ LOW TEMPERATURE: {temp:.1f}°C")
                
                if humidity > config.AUTO_HUMIDITY_HIGH:
                    self.add_log(f"⚠️ HIGH HUMIDITY: {humidity:.1f}%RH")
                elif humidity < config.AUTO_HUMIDITY_LOW:
                    self.add_log(f"⚠️ LOW HUMIDITY: {humidity:.1f}%RH")
            
            else:
                self.add_log("❌ Failed to read sensor data")
        
        except Exception as e:
            self.add_log(f"❌ Read error: {str(e)}")
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.clear()
        self.add_log("🗑️ Log cleared")
    
    def add_log(self, message):
        """Thêm log message"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Xử lý khi đóng cửa sổ"""
        if self.read_timer.isActive():
            self.read_timer.stop()
        
        if self.rs485:
            self.rs485.disconnect()
        
        event.accept()


def main():
    """Hàm main"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SensorDisplayWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
