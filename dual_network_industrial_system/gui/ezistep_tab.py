"""
Tab điều khiển động cơ Ezi-STEP Plus-R
Hỗ trợ Jog, Move Absolute, Homing và hiển thị trạng thái
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                             QTextEdit, QRadioButton, QButtonGroup, QLCDNumber)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class EziStepTab(QWidget):
    """Tab điều khiển động cơ Ezi-STEP Plus-R"""
    
    def __init__(self, driver, driver_config, gui_config):
        super().__init__()
        self.driver = driver
        self.driver_config = driver_config
        self.gui_config = gui_config
        
        self.init_ui()
        
        # Timer để cập nhật trạng thái
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # ===== CONTROL GROUP =====
        control_group = self._create_control_group()
        layout.addWidget(control_group)
        
        # ===== STATUS GROUP =====
        status_group = self._create_status_group()
        layout.addWidget(status_group)
        
        # ===== SERVO GROUP =====
        servo_group = self._create_servo_group()
        layout.addWidget(servo_group)
        
        # ===== JOG GROUP =====
        jog_group = self._create_jog_group()
        layout.addWidget(jog_group)
        
        # ===== MOVE GROUP =====
        move_group = self._create_move_group()
        layout.addWidget(move_group, 1)
        
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
    
    def _create_status_group(self):
        """Tạo nhóm hiển thị trạng thái"""
        group = QGroupBox("Trạng Thái Động Cơ")
        layout = QHBoxLayout()
        
        # Position display
        pos_layout = QVBoxLayout()
        pos_label = QLabel("📍 VỊ TRÍ")
        pos_label.setAlignment(Qt.AlignCenter)
        pos_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4CAF50;")
        
        self.lcd_position = QLCDNumber()
        self.lcd_position.setDigitCount(8)
        self.lcd_position.setMinimumHeight(60)
        self.lcd_position.setStyleSheet("""
            QLCDNumber {
                background-color: #1E1E1E;
                color: #66BB6A;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
        """)
        self.lcd_position.display("0")
        
        pos_unit = QLabel("pulse")
        pos_unit.setAlignment(Qt.AlignCenter)
        pos_unit.setStyleSheet("font-size: 10pt;")
        
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(self.lcd_position)
        pos_layout.addWidget(pos_unit)
        
        # Status display
        status_layout = QVBoxLayout()
        status_label = QLabel("⚙️ TRẠNG THÁI")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FF9800;")
        
        self.lbl_motor_status = QLabel("IDLE")
        self.lbl_motor_status.setAlignment(Qt.AlignCenter)
        self.lbl_motor_status.setStyleSheet("""
            QLabel {
                font-size: 20pt;
                font-weight: bold;
                padding: 10px;
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                border-radius: 5px;
                color: #F57C00;
            }
        """)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.lbl_motor_status)
        status_layout.addStretch()
        
        layout.addLayout(pos_layout)
        layout.addLayout(status_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_servo_group(self):
        """Tạo nhóm điều khiển Servo"""
        group = QGroupBox("Điều Khiển Servo")
        layout = QHBoxLayout()
        
        # Servo ON
        self.btn_servo_on = QPushButton("⚡ SERVO ON")
        self.btn_servo_on.setMinimumHeight(50)
        self.btn_servo_on.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.gui_config['colors']['success']};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #388E3C;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
            }}
        """)
        self.btn_servo_on.clicked.connect(self.on_servo_on)
        self.btn_servo_on.setEnabled(False)
        
        # Servo OFF
        self.btn_servo_off = QPushButton("⚫ SERVO OFF")
        self.btn_servo_off.setMinimumHeight(50)
        self.btn_servo_off.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_servo_off.clicked.connect(self.on_servo_off)
        self.btn_servo_off.setEnabled(False)
        
        # Stop
        self.btn_stop = QPushButton("🛑 STOP")
        self.btn_stop.setMinimumHeight(50)
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.gui_config['colors']['danger']};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #C62828;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
            }}
        """)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_stop.setEnabled(False)
        
        # Homing
        self.btn_homing = QPushButton("🏠 HOMING")
        self.btn_homing.setMinimumHeight(50)
        self.btn_homing.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.gui_config['colors']['warning']};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F57C00;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
            }}
        """)
        self.btn_homing.clicked.connect(self.on_homing)
        self.btn_homing.setEnabled(False)
        
        layout.addWidget(self.btn_servo_on)
        layout.addWidget(self.btn_servo_off)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_homing)
        
        group.setLayout(layout)
        return group
    
    def _create_jog_group(self):
        """Tạo nhóm điều khiển Jog"""
        group = QGroupBox("Chế Độ Jog (Chạy Liên Tục)")
        layout = QHBoxLayout()
        
        # Speed input
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Tốc độ (pps):")
        self.spin_jog_speed = QSpinBox()
        self.spin_jog_speed.setRange(100, 10000)
        self.spin_jog_speed.setValue(1000)
        self.spin_jog_speed.setSingleStep(100)
        self.spin_jog_speed.setMinimumHeight(40)
        self.spin_jog_speed.setStyleSheet("font-size: 12pt;")
        
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.spin_jog_speed)
        
        # Direction buttons
        self.btn_jog_cw = QPushButton("➡️ JOG CW")
        self.btn_jog_cw.setMinimumHeight(60)
        self.btn_jog_cw.setStyleSheet("""
            QPushButton {
                background-color: #03A9F4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0288D1;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_jog_cw.clicked.connect(lambda: self.on_jog(1))
        self.btn_jog_cw.setEnabled(False)
        
        self.btn_jog_ccw = QPushButton("⬅️ JOG CCW")
        self.btn_jog_ccw.setMinimumHeight(60)
        self.btn_jog_ccw.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0097A7;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_jog_ccw.clicked.connect(lambda: self.on_jog(0))
        self.btn_jog_ccw.setEnabled(False)
        
        layout.addLayout(speed_layout, 1)
        layout.addWidget(self.btn_jog_cw, 2)
        layout.addWidget(self.btn_jog_ccw, 2)
        
        group.setLayout(layout)
        return group
    
    def _create_move_group(self):
        """Tạo nhóm điều khiển Move"""
        group = QGroupBox("Di Chuyển Chính Xác")
        main_layout = QHBoxLayout()
        
        # Absolute Move
        abs_layout = QVBoxLayout()
        abs_label = QLabel("Di chuyển Tuyệt đối:")
        abs_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        
        abs_input_layout = QHBoxLayout()
        self.spin_abs_pos = QSpinBox()
        self.spin_abs_pos.setRange(
            self.driver_config['limits']['min_position'],
            self.driver_config['limits']['max_position']
        )
        self.spin_abs_pos.setValue(0)
        self.spin_abs_pos.setSingleStep(1000)
        self.spin_abs_pos.setMinimumHeight(35)
        self.spin_abs_pos.setStyleSheet("font-size: 11pt;")
        
        self.spin_abs_speed = QSpinBox()
        self.spin_abs_speed.setRange(100, 10000)
        self.spin_abs_speed.setValue(2000)
        self.spin_abs_speed.setSingleStep(100)
        self.spin_abs_speed.setMinimumHeight(35)
        self.spin_abs_speed.setStyleSheet("font-size: 11pt;")
        
        abs_input_layout.addWidget(QLabel("Vị trí (pulse):"))
        abs_input_layout.addWidget(self.spin_abs_pos)
        abs_input_layout.addWidget(QLabel("Tốc độ (pps):"))
        abs_input_layout.addWidget(self.spin_abs_speed)
        
        self.btn_move_abs = QPushButton("▶️ Di chuyển Tuyệt đối")
        self.btn_move_abs.setMinimumHeight(45)
        self.btn_move_abs.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_move_abs.clicked.connect(self.on_move_absolute)
        self.btn_move_abs.setEnabled(False)
        
        abs_layout.addWidget(abs_label)
        abs_layout.addLayout(abs_input_layout)
        abs_layout.addWidget(self.btn_move_abs)
        
        # Relative Move
        rel_layout = QVBoxLayout()
        rel_label = QLabel("Di chuyển Tương đối:")
        rel_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        
        rel_input_layout = QHBoxLayout()
        self.spin_rel_dist = QSpinBox()
        self.spin_rel_dist.setRange(-100000, 100000)
        self.spin_rel_dist.setValue(0)
        self.spin_rel_dist.setSingleStep(1000)
        self.spin_rel_dist.setMinimumHeight(35)
        self.spin_rel_dist.setStyleSheet("font-size: 11pt;")
        
        self.spin_rel_speed = QSpinBox()
        self.spin_rel_speed.setRange(100, 10000)
        self.spin_rel_speed.setValue(2000)
        self.spin_rel_speed.setSingleStep(100)
        self.spin_rel_speed.setMinimumHeight(35)
        self.spin_rel_speed.setStyleSheet("font-size: 11pt;")
        
        rel_input_layout.addWidget(QLabel("Khoảng cách (pulse):"))
        rel_input_layout.addWidget(self.spin_rel_dist)
        rel_input_layout.addWidget(QLabel("Tốc độ (pps):"))
        rel_input_layout.addWidget(self.spin_rel_speed)
        
        self.btn_move_rel = QPushButton("▶️ Di chuyển Tương đối")
        self.btn_move_rel.setMinimumHeight(45)
        self.btn_move_rel.setStyleSheet("""
            QPushButton {
                background-color: #673AB7;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #512DA8;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_move_rel.clicked.connect(self.on_move_relative)
        self.btn_move_rel.setEnabled(False)
        
        rel_layout.addWidget(rel_label)
        rel_layout.addLayout(rel_input_layout)
        rel_layout.addWidget(self.btn_move_rel)
        
        main_layout.addLayout(abs_layout)
        main_layout.addLayout(rel_layout)
        
        group.setLayout(main_layout)
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
        self.log_message("Đang kết nối tới Ezi-STEP...")
        
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
            
            # Enable servo controls
            self.btn_servo_on.setEnabled(True)
            self.btn_servo_off.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.btn_homing.setEnabled(True)
            
            self.log_message(f"✅ Kết nối thành công trên {self.driver.config['port']}")
            
            # Bắt đầu cập nhật trạng thái
            self.status_timer.start(500)
        else:
            self.log_message("❌ Kết nối thất bại!")
    
    def on_disconnect(self):
        """Xử lý ngắt kết nối"""
        self.status_timer.stop()
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
        
        # Disable all controls
        self.btn_servo_on.setEnabled(False)
        self.btn_servo_off.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_homing.setEnabled(False)
        self.btn_jog_cw.setEnabled(False)
        self.btn_jog_ccw.setEnabled(False)
        self.btn_move_abs.setEnabled(False)
        self.btn_move_rel.setEnabled(False)
        
        self.log_message("⚫ Đã ngắt kết nối")
    
    def on_servo_on(self):
        """Bật Servo"""
        if self.driver.servo_on():
            self.log_message("✅ Servo đã bật")
            self.lbl_motor_status.setText("READY")
            
            # Enable movement controls
            self.btn_jog_cw.setEnabled(True)
            self.btn_jog_ccw.setEnabled(True)
            self.btn_move_abs.setEnabled(True)
            self.btn_move_rel.setEnabled(True)
        else:
            self.log_message("❌ Không thể bật Servo")
    
    def on_servo_off(self):
        """Tắt Servo"""
        if self.driver.servo_off():
            self.log_message("⚫ Servo đã tắt")
            self.lbl_motor_status.setText("SERVO OFF")
            
            # Disable movement controls
            self.btn_jog_cw.setEnabled(False)
            self.btn_jog_ccw.setEnabled(False)
            self.btn_move_abs.setEnabled(False)
            self.btn_move_rel.setEnabled(False)
        else:
            self.log_message("❌ Không thể tắt Servo")
    
    def on_stop(self):
        """Dừng động cơ"""
        if self.driver.stop():
            self.log_message("🛑 Động cơ đã dừng")
            self.lbl_motor_status.setText("STOPPED")
        else:
            self.log_message("❌ Không thể dừng động cơ")
    
    def on_jog(self, direction: int):
        """Chạy Jog"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔴 GUI on_jog() được gọi! direction={direction}")
        
        speed = self.spin_jog_speed.value()
        dir_text = "CW" if direction == 1 else "CCW"
        logger.info(f"🔴 Chuẩn bị gọi driver.jog_move(speed={speed}, direction={direction})")
        
        if self.driver.jog_move(speed, direction):
            self.log_message(f"▶️ Jog {dir_text} @ {speed} pps")
            self.lbl_motor_status.setText(f"JOG {dir_text}")
        else:
            self.log_message(f"❌ Không thể chạy Jog {dir_text}")
    
    def on_move_absolute(self):
        """Di chuyển tuyệt đối"""
        position = self.spin_abs_pos.value()
        speed = self.spin_abs_speed.value()
        
        if self.driver.move_absolute(position, speed):
            self.log_message(f"▶️ Move Absolute: {position} @ {speed} pps")
            self.lbl_motor_status.setText("MOVING")
        else:
            self.log_message("❌ Không thể di chuyển")
    
    def on_move_relative(self):
        """Di chuyển tương đối"""
        distance = self.spin_rel_dist.value()
        speed = self.spin_rel_speed.value()
        
        if self.driver.move_relative(distance, speed):
            self.log_message(f"▶️ Move Relative: {distance:+d} @ {speed} pps")
            self.lbl_motor_status.setText("MOVING")
        else:
            self.log_message("❌ Không thể di chuyển")
    
    def on_homing(self):
        """Thực hiện Homing"""
        if self.driver.homing():
            self.log_message("🏠 Bắt đầu Homing...")
            self.lbl_motor_status.setText("HOMING")
        else:
            self.log_message("❌ Không thể bắt đầu Homing")
    
    def update_status(self):
        """Cập nhật trạng thái động cơ"""
        position = self.driver.read_position()
        if position is not None:
            self.lcd_position.display(str(position))
    
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
        self.status_timer.stop()
        if self.driver.is_connected:
            self.driver.disconnect()
