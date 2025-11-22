"""
Tab điều khiển cảm biến SHT20
Hiển thị nhiệt độ, độ ẩm và đồ thị realtime
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QLCDNumber, QTextEdit)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg
from collections import deque
import logging

logger = logging.getLogger(__name__)


class SHT20Tab(QWidget):
    """Tab điều khiển và giám sát cảm biến SHT20"""
    
    # Signal để gửi dữ liệu cho automation tab
    data_updated = pyqtSignal(float, float)  # (temperature, humidity)
    
    def __init__(self, driver, driver_config, gui_config):
        super().__init__()
        self.driver = driver
        self.driver_config = driver_config
        self.gui_config = gui_config
        
        # Data buffers cho đồ thị
        self.temp_data = deque(maxlen=gui_config['graph']['max_points'])
        self.humid_data = deque(maxlen=gui_config['graph']['max_points'])
        self.time_data = deque(maxlen=gui_config['graph']['max_points'])
        self.time_counter = 0
        
        self.init_ui()
        
        # Timer để đọc dữ liệu
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.update_sensor_data)
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # ===== CONTROL GROUP =====
        control_group = self._create_control_group()
        layout.addWidget(control_group)
        
        # ===== DISPLAY GROUP =====
        display_group = self._create_display_group()
        layout.addWidget(display_group)
        
        # ===== GRAPH GROUP =====
        graph_group = self._create_graph_group()
        layout.addWidget(graph_group, 2)  # Stretch factor 2
        
        # ===== LOG GROUP =====
        log_group = self._create_log_group()
        layout.addWidget(log_group, 1)
        
        self.setLayout(layout)
    
    def _create_control_group(self):
        """Tạo nhóm điều khiển kết nối"""
        group = QGroupBox("Điều Khiển Kết Nối")
        layout = QHBoxLayout()
        
        # Connect button
        self.btn_connect = QPushButton("🔌 Kết Nối")
        self.btn_connect.setMinimumHeight(50)
        self.btn_connect.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.gui_config['colors']['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
            }}
        """)
        self.btn_connect.clicked.connect(self.on_connect)
        
        # Disconnect button
        self.btn_disconnect = QPushButton("🔌 Ngắt Kết Nối")
        self.btn_disconnect.setMinimumHeight(50)
        self.btn_disconnect.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.gui_config['colors']['danger']};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #D32F2F;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
            }}
        """)
        self.btn_disconnect.clicked.connect(self.on_disconnect)
        self.btn_disconnect.setEnabled(False)
        
        # Status label
        self.lbl_status = QLabel("⚫ Chưa kết nối")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding: 10px;
                background-color: #EEEEEE;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.btn_connect, 2)
        layout.addWidget(self.btn_disconnect, 2)
        layout.addWidget(self.lbl_status, 3)
        
        group.setLayout(layout)
        return group
    
    def _create_display_group(self):
        """Tạo nhóm hiển thị dữ liệu"""
        group = QGroupBox("Dữ Liệu Cảm Biến")
        layout = QHBoxLayout()
        
        # Temperature display
        temp_layout = QVBoxLayout()
        temp_label = QLabel("🌡️ NHIỆT ĐỘ")
        temp_label.setAlignment(Qt.AlignCenter)
        temp_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #F44336;")
        
        self.lcd_temp = QLCDNumber()
        self.lcd_temp.setDigitCount(5)
        self.lcd_temp.setMinimumHeight(80)
        self.lcd_temp.setStyleSheet("""
            QLCDNumber {
                background-color: #1E1E1E;
                color: #FF5252;
                border: 2px solid #F44336;
                border-radius: 5px;
            }
        """)
        self.lcd_temp.display("--.-")
        
        temp_unit = QLabel("°C")
        temp_unit.setAlignment(Qt.AlignCenter)
        temp_unit.setStyleSheet("font-size: 12pt; font-weight: bold;")
        
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.lcd_temp)
        temp_layout.addWidget(temp_unit)
        
        # Humidity display
        humid_layout = QVBoxLayout()
        humid_label = QLabel("💧 ĐỘ ẨM")
        humid_label.setAlignment(Qt.AlignCenter)
        humid_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2196F3;")
        
        self.lcd_humid = QLCDNumber()
        self.lcd_humid.setDigitCount(5)
        self.lcd_humid.setMinimumHeight(80)
        self.lcd_humid.setStyleSheet("""
            QLCDNumber {
                background-color: #1E1E1E;
                color: #42A5F5;
                border: 2px solid #2196F3;
                border-radius: 5px;
            }
        """)
        self.lcd_humid.display("--.-")
        
        humid_unit = QLabel("%RH")
        humid_unit.setAlignment(Qt.AlignCenter)
        humid_unit.setStyleSheet("font-size: 12pt; font-weight: bold;")
        
        humid_layout.addWidget(humid_label)
        humid_layout.addWidget(self.lcd_humid)
        humid_layout.addWidget(humid_unit)
        
        layout.addLayout(temp_layout)
        layout.addLayout(humid_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_graph_group(self):
        """Tạo nhóm đồ thị realtime"""
        group = QGroupBox("Đồ Thị Theo Thời Gian")
        layout = QHBoxLayout()  # Đổi sang Horizontal để 2 đồ thị cạnh nhau
        
        # ===== TEMPERATURE GRAPH =====
        self.temp_plot = pg.PlotWidget()
        self.temp_plot.setBackground('w')
        self.temp_plot.setTitle("🌡️ NHIỆT ĐỘ", color='#F44336', size='12pt', bold=True)
        self.temp_plot.setLabel('left', 'T (°C)', color='#212121', size='10pt')
        self.temp_plot.setLabel('bottom', 'Thời gian (s)', color='#212121', size='10pt')
        self.temp_plot.showGrid(x=True, y=True, alpha=0.3)
        self.temp_plot.setMinimumHeight(180)
        self.temp_plot.setMaximumHeight(250)
        
        # Temperature curve với đường cong mượt
        self.temp_curve = self.temp_plot.plot(
            pen=pg.mkPen(color='#F44336', width=2.5, style=pg.QtCore.Qt.SolidLine),
            fillLevel=0,
            brush=pg.mkBrush(255, 67, 54, 50),  # Tô màu nhạt phía dưới
            antialias=True  # Làm mượt đường cong
        )
        
        # ===== HUMIDITY GRAPH =====
        self.humid_plot = pg.PlotWidget()
        self.humid_plot.setBackground('w')
        self.humid_plot.setTitle("💧 ĐỘ ẨM", color='#2196F3', size='12pt', bold=True)
        self.humid_plot.setLabel('left', 'H (%RH)', color='#212121', size='10pt')
        self.humid_plot.setLabel('bottom', 'Thời gian (s)', color='#212121', size='10pt')
        self.humid_plot.showGrid(x=True, y=True, alpha=0.3)
        self.humid_plot.setMinimumHeight(180)
        self.humid_plot.setMaximumHeight(250)
        
        # Humidity curve với đường cong mượt
        self.humid_curve = self.humid_plot.plot(
            pen=pg.mkPen(color='#2196F3', width=2.5, style=pg.QtCore.Qt.SolidLine),
            fillLevel=0,
            brush=pg.mkBrush(33, 150, 243, 50),  # Tô màu nhạt phía dưới
            antialias=True  # Làm mượt đường cong
        )
        
        # Add to layout (2 đồ thị cạnh nhau)
        layout.addWidget(self.temp_plot)
        layout.addWidget(self.humid_plot)
        
        group.setLayout(layout)
        return group
    
    def _create_log_group(self):
        """Tạo nhóm hiển thị log"""
        group = QGroupBox("Nhật Ký Hoạt Động")
        layout = QVBoxLayout()
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(120)
        self.txt_log.setStyleSheet("""
            QTextEdit {
                background-color: #263238;
                color: #AAAAAA;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                border: 1px solid #555;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(self.txt_log)
        group.setLayout(layout)
        return group
    
    def on_connect(self):
        """Xử lý kết nối"""
        self.log_message("Đang kết nối tới SHT20...")
        
        if self.driver.connect():
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.lbl_status.setText("🟢 Đã kết nối")
            self.lbl_status.setStyleSheet("""
                QLabel {
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 10px;
                    background-color: #C8E6C9;
                    border-radius: 5px;
                    color: #2E7D32;
                }
            """)
            self.log_message(f"✅ Kết nối thành công trên {self.driver.config['port']}")
            
            # Bắt đầu đọc dữ liệu
            interval = self.driver_config['read_interval']
            self.read_timer.start(interval)
            self.log_message(f"🔄 Bắt đầu đọc dữ liệu mỗi {interval}ms")
        else:
            self.log_message("❌ Kết nối thất bại!")
    
    def on_disconnect(self):
        """Xử lý ngắt kết nối"""
        self.read_timer.stop()
        self.driver.disconnect()
        
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.lbl_status.setText("⚫ Chưa kết nối")
        self.lbl_status.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding: 10px;
                background-color: #EEEEEE;
                border-radius: 5px;
            }
        """)
        self.log_message("⚫ Đã ngắt kết nối")
    
    def update_sensor_data(self):
        """Cập nhật dữ liệu cảm biến"""
        try:
            temp, humid = self.driver.read_sensor_data()
            
            if temp is not None and humid is not None:
                # Cập nhật LCD
                self.lcd_temp.display(f"{temp:.1f}")
                self.lcd_humid.display(f"{humid:.1f}")
                
                # Phát signal cho automation tab
                self.data_updated.emit(temp, humid)
                
                # Cập nhật đồ thị
                self.time_counter += 1
                self.time_data.append(self.time_counter)
                self.temp_data.append(temp)
                self.humid_data.append(humid)
                
                # Tạo đường cong mượt hơn bằng cách vẽ với connect='finite'
                self.temp_curve.setData(
                    list(self.time_data), 
                    list(self.temp_data),
                    connect='finite'
                )
                
                self.humid_curve.setData(
                    list(self.time_data), 
                    list(self.humid_data),
                    connect='finite'
                )
                
                # Auto-scroll X axis (hiển thị 50 điểm gần nhất)
                if len(self.time_data) > 50:
                    x_min = self.time_data[-50]
                    x_max = self.time_data[-1]
                    self.temp_plot.setXRange(x_min, x_max, padding=0.02)
                    self.humid_plot.setXRange(x_min, x_max, padding=0.02)
                
                # Auto-scale Y với padding
                if len(self.temp_data) >= 2:
                    temp_list = list(self.temp_data)
                    recent_temp = temp_list[-50:] if len(temp_list) > 50 else temp_list
                    temp_min = min(recent_temp)
                    temp_max = max(recent_temp)
                    temp_range = temp_max - temp_min if temp_max > temp_min else 1
                    self.temp_plot.setYRange(temp_min - temp_range*0.2, temp_max + temp_range*0.2)
                    
                if len(self.humid_data) >= 2:
                    humid_list = list(self.humid_data)
                    recent_humid = humid_list[-50:] if len(humid_list) > 50 else humid_list
                    humid_min = min(recent_humid)
                    humid_max = max(recent_humid)
                    humid_range = humid_max - humid_min if humid_max > humid_min else 1
                    self.humid_plot.setYRange(humid_min - humid_range*0.2, humid_max + humid_range*0.2)
                
                # Ghi log mỗi 5 lần đọc (5 giây)
                if self.time_counter % 5 == 0:
                    self.log_message(f"📊 Nhiệt độ: {temp:.1f}°C | Độ ẩm: {humid:.1f}%RH")
            else:
                self.log_message("⚠️ Không đọc được dữ liệu từ cảm biến")
        except Exception as e:
            self.log_message(f"❌ Lỗi đọc dữ liệu: {str(e)}")
    
    def log_message(self, message: str):
        """Thêm message vào log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.append(f"[{timestamp}] {message}")
        
        # Scroll to bottom
        scrollbar = self.txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def cleanup(self):
        """Dọn dẹp khi đóng"""
        self.read_timer.stop()
        if self.driver.is_connected:
            self.driver.disconnect()
