"""
Tab điều khiển động cơ Ezi-STEP Plus-R - SIMPLE CLEAN LAYOUT
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QSpinBox, QLCDNumber,
                             QTextEdit, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
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
        """Khởi tạo giao diện - SIMPLE & CLEAN"""
        main = QVBoxLayout()
        main.setSpacing(5)
        main.setContentsMargins(5, 5, 5, 5)
        
        # ROW 1: Connection
        conn_group = QGroupBox("Kết Nối")
        conn_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("🔌 Kết Nối")
        self.btn_connect.setMinimumHeight(40)
        self.btn_connect.clicked.connect(self.on_connect)
        
        self.btn_disconnect = QPushButton("🔌 Ngắt Kết Nối")
        self.btn_disconnect.setMinimumHeight(40)
        self.btn_disconnect.clicked.connect(self.on_disconnect)
        self.btn_disconnect.setEnabled(False)
        
        self.lbl_status = QLabel("⚫ Chưa kết nối")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)
        conn_layout.addWidget(self.lbl_status, 1)
        conn_group.setLayout(conn_layout)
        main.addWidget(conn_group)
        
        # ROW 2: Status Display
        status_layout = QHBoxLayout()
        
        # LCD Position
        lcd_group = QGroupBox("📍 Vị Trí")
        lcd_layout = QVBoxLayout()
        self.lcd_position = QLCDNumber()
        self.lcd_position.setDigitCount(8)
        self.lcd_position.setMinimumHeight(60)
        self.lcd_position.setStyleSheet("background-color: #000; color: #0F0; border: 2px solid #0F0;")
        lcd_layout.addWidget(self.lcd_position)
        lcd_layout.addWidget(QLabel("pulse", alignment=Qt.AlignCenter))
        lcd_group.setLayout(lcd_layout)
        status_layout.addWidget(lcd_group)
        
        # Motor Status
        motor_group = QGroupBox("⚡ Trạng Thái")
        motor_layout = QVBoxLayout()
        self.lbl_motor_status = QLabel("⏸ IDLE")
        self.lbl_motor_status.setAlignment(Qt.AlignCenter)
        self.lbl_motor_status.setMinimumHeight(60)
        self.lbl_motor_status.setStyleSheet("font-size: 16pt; font-weight: bold; background: #EEE; border: 2px solid #999;")
        motor_layout.addWidget(self.lbl_motor_status)
        motor_group.setLayout(motor_layout)
        status_layout.addWidget(motor_group)
        
        # Servo Indicator
        servo_group = QGroupBox("🟢 Servo")
        servo_layout = QVBoxLayout()
        self.lbl_servo_state = QLabel("🔴 OFF")
        self.lbl_servo_state.setAlignment(Qt.AlignCenter)
        self.lbl_servo_state.setMinimumHeight(30)
        self.lbl_speed_display = QLabel("⚡ 0 pps")
        self.lbl_speed_display.setAlignment(Qt.AlignCenter)
        self.lbl_speed_display.setMinimumHeight(30)
        servo_layout.addWidget(self.lbl_servo_state)
        servo_layout.addWidget(self.lbl_speed_display)
        servo_group.setLayout(servo_layout)
        status_layout.addWidget(servo_group)
        
        main.addLayout(status_layout)
        
        # ROW 3: Control Buttons (3 columns)
        control_layout = QHBoxLayout()
        
        # COL 1: Servo Controls
        servo_ctrl_group = QGroupBox("⚙️ Servo")
        servo_ctrl_layout = QVBoxLayout()
        
        self.btn_servo_on = QPushButton("⚡ ON")
        self.btn_servo_on.setMinimumHeight(50)
        self.btn_servo_on.setStyleSheet("background: #4CAF50; color: white; font-weight: bold; font-size: 11pt;")
        self.btn_servo_on.clicked.connect(self.on_servo_on)
        self.btn_servo_on.setEnabled(False)
        
        self.btn_servo_off = QPushButton("⏸ OFF")
        self.btn_servo_off.setMinimumHeight(50)
        self.btn_servo_off.setStyleSheet("background: #FF5722; color: white; font-weight: bold; font-size: 11pt;")
        self.btn_servo_off.clicked.connect(self.on_servo_off)
        self.btn_servo_off.setEnabled(False)
        
        self.btn_stop = QPushButton("🛑 STOP")
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setStyleSheet("background: #F44336; color: white; font-weight: bold;")
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_stop.setEnabled(False)
        
        self.btn_home = QPushButton("🏠 HOME")
        self.btn_home.setMinimumHeight(40)
        self.btn_home.setStyleSheet("background: #9C27B0; color: white; font-weight: bold;")
        self.btn_home.clicked.connect(self.on_home)
        self.btn_home.setEnabled(False)
        
        servo_ctrl_layout.addWidget(self.btn_servo_on)
        servo_ctrl_layout.addWidget(self.btn_servo_off)
        servo_ctrl_layout.addWidget(self.btn_stop)
        servo_ctrl_layout.addWidget(self.btn_home)
        servo_ctrl_group.setLayout(servo_ctrl_layout)
        control_layout.addWidget(servo_ctrl_group)
        
        # COL 2: JOG Controls
        jog_group = QGroupBox("🎮 JOG")
        jog_layout = QVBoxLayout()
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Tốc độ:"))
        self.spin_jog_speed = QSpinBox()
        self.spin_jog_speed.setRange(1000, 50000)
        self.spin_jog_speed.setValue(20000)
        self.spin_jog_speed.setSingleStep(1000)
        speed_layout.addWidget(self.spin_jog_speed)
        speed_layout.addWidget(QLabel("pps"))
        jog_layout.addLayout(speed_layout)
        
        jog_buttons = QHBoxLayout()
        self.btn_jog_ccw = QPushButton("⬅ JOG-")
        self.btn_jog_ccw.setMinimumHeight(50)
        self.btn_jog_ccw.setStyleSheet("background: #2196F3; color: white; font-weight: bold;")
        self.btn_jog_ccw.pressed.connect(self.on_jog_ccw_pressed)
        self.btn_jog_ccw.released.connect(self.on_jog_released)
        self.btn_jog_ccw.setEnabled(False)
        
        self.btn_jog_cw = QPushButton("JOG+ ➡")
        self.btn_jog_cw.setMinimumHeight(50)
        self.btn_jog_cw.setStyleSheet("background: #2196F3; color: white; font-weight: bold;")
        self.btn_jog_cw.pressed.connect(self.on_jog_cw_pressed)
        self.btn_jog_cw.released.connect(self.on_jog_released)
        self.btn_jog_cw.setEnabled(False)
        
        jog_buttons.addWidget(self.btn_jog_ccw)
        jog_buttons.addWidget(self.btn_jog_cw)
        jog_layout.addLayout(jog_buttons)
        jog_group.setLayout(jog_layout)
        control_layout.addWidget(jog_group)
        
        # COL 3: Move Controls
        move_group = QGroupBox("📍 Move")
        move_layout = QVBoxLayout()
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Vị trí:"))
        self.spin_cmd_pos = QSpinBox()
        self.spin_cmd_pos.setRange(-1000000, 1000000)
        self.spin_cmd_pos.setValue(10000)
        self.spin_cmd_pos.setSingleStep(1000)
        pos_layout.addWidget(self.spin_cmd_pos)
        pos_layout.addWidget(QLabel("pulse"))
        move_layout.addLayout(pos_layout)
        
        # Tốc độ chung cho ABS, DEC, INC
        move_speed_layout = QHBoxLayout()
        move_speed_layout.addWidget(QLabel("Tốc độ:"))
        self.spin_move_speed = QSpinBox()
        self.spin_move_speed.setRange(1000, 50000)
        self.spin_move_speed.setValue(10000)
        self.spin_move_speed.setSingleStep(1000)
        move_speed_layout.addWidget(self.spin_move_speed)
        move_speed_layout.addWidget(QLabel("pps"))
        move_layout.addLayout(move_speed_layout)
        
        self.btn_abs_move = QPushButton("📍 ABS")
        self.btn_abs_move.setMinimumHeight(35)
        self.btn_abs_move.setStyleSheet("background: #9C27B0; color: white; font-weight: bold;")
        self.btn_abs_move.clicked.connect(self.on_abs_move)
        self.btn_abs_move.setEnabled(False)
        move_layout.addWidget(self.btn_abs_move)
        
        # Xóa ô tốc độ riêng DEC/INC (dùng chung spin_move_speed)
        self.spin_dec_inc_speed = self.spin_move_speed  # Alias để code tương thích
        
        dec_inc_layout = QHBoxLayout()
        self.btn_dec_move = QPushButton("⬅ DEC")
        self.btn_dec_move.setMinimumHeight(35)
        self.btn_dec_move.setStyleSheet("background: #3F51B5; color: white; font-weight: bold;")
        self.btn_dec_move.clicked.connect(self.on_dec_move)
        self.btn_dec_move.setEnabled(False)
        
        self.btn_inc_move = QPushButton("INC ➡")
        self.btn_inc_move.setMinimumHeight(35)
        self.btn_inc_move.setStyleSheet("background: #3F51B5; color: white; font-weight: bold;")
        self.btn_inc_move.clicked.connect(self.on_inc_move)
        self.btn_inc_move.setEnabled(False)
        
        dec_inc_layout.addWidget(self.btn_dec_move)
        dec_inc_layout.addWidget(self.btn_inc_move)
        move_layout.addLayout(dec_inc_layout)
        
        move_group.setLayout(move_layout)
        control_layout.addWidget(move_group)
        
        main.addLayout(control_layout)
        
        # ROW 4: Log
        log_group = QGroupBox("📋 Nhật Ký")
        log_layout = QVBoxLayout()
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(150)
        log_layout.addWidget(self.txt_log)
        log_group.setLayout(log_layout)
        main.addWidget(log_group)
        
        # Dummy labels for compatibility
        self.lbl_cmd_pos_display = QLabel("0")
        self.lbl_actual_pos_display = QLabel("0")
        self.lbl_actual_vel_display = QLabel("0")
        self.lbl_rpm_display = QLabel("0")
        self.lbl_pos_error_display = QLabel("0")
        self.btn_jog_stop = None
        self.btn_clear_position = None
        self.btn_minus_limit = None
        self.btn_plus_limit = None
        self.btn_homing = None
        
        self.setLayout(main)
    
    # ==================== EVENT HANDLERS ====================
    
    def on_connect(self):
        """Kết nối motor"""
        if self.driver.connect():
            self.log_message("✅ Đã kết nối motor")
            
            # Tự động reset vị trí về 0
            if self.driver.clear_position():
                self.log_message("🏠 Đã reset vị trí về 0")
            
            self.lbl_status.setText("🟢 Đã kết nối")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.btn_servo_on.setEnabled(True)
            self.status_timer.start(500)
        else:
            self.log_message("❌ Không thể kết nối motor")
    
    def on_disconnect(self):
        """Ngắt kết nối motor"""
        self.status_timer.stop()
        self.driver.disconnect()
        self.log_message("⚫ Đã ngắt kết nối")
        self.lbl_status.setText("⚫ Chưa kết nối")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_servo_on.setEnabled(False)
        self.btn_servo_off.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_jog_cw.setEnabled(False)
        self.btn_jog_ccw.setEnabled(False)
        self.btn_abs_move.setEnabled(False)
        self.btn_dec_move.setEnabled(False)
        self.btn_inc_move.setEnabled(False)
        self.btn_move_rel.setEnabled(False)
    
    def on_servo_on(self):
        """Bật Servo"""
        if self.driver.servo_on():
            self.log_message("✅ Servo ON")
            self.lbl_servo_state.setText("🟢 ON")
            self.lbl_servo_state.setStyleSheet("background: #E8F5E9; border: 2px solid #4CAF50; color: #2E7D32; font-weight: bold; padding: 5px;")
            self.lbl_motor_status.setText("⚡ READY")
            self.btn_servo_off.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.btn_home.setEnabled(True)
            self.btn_jog_cw.setEnabled(True)
            self.btn_jog_ccw.setEnabled(True)
            self.btn_abs_move.setEnabled(True)
            self.btn_dec_move.setEnabled(True)
            self.btn_inc_move.setEnabled(True)
    
    def on_servo_off(self):
        """Tắt Servo"""
        if self.driver.servo_off():
            self.log_message("⚫ Servo OFF")
            self.lbl_servo_state.setText("🔴 OFF")
            self.lbl_servo_state.setStyleSheet("background: #FFEBEE; border: 2px solid #EF5350; color: #C62828; font-weight: bold; padding: 5px;")
            self.lbl_motor_status.setText("⏸ SERVO OFF")
            self.btn_home.setEnabled(False)
            self.btn_jog_cw.setEnabled(False)
            self.btn_jog_ccw.setEnabled(False)
            self.btn_abs_move.setEnabled(False)
            self.btn_dec_move.setEnabled(False)
            self.btn_inc_move.setEnabled(False)
    
    def on_stop(self):
        """Dừng motor"""
        if self.driver.stop():
            self.log_message("🛑 Đã dừng motor")
            self.lbl_motor_status.setText("⏸ STOPPED")
    
    def on_home(self):
        """Home - Di chuyển động cơ về vị trí 0"""
        home_speed = 50000  # ⚠️ Tốc độ Home cố định 50000 pps (nhanh)
        self.log_message(f"🏠 Đang Home về vị trí 0 @ {home_speed} pps...")
        
        # Di chuyển tuyệt đối về vị trí 0
        if self.driver.move_absolute(0, home_speed):
            self.log_message("✅ Home hoàn tất - Động cơ đã về vị trí 0")
        else:
            self.log_message("❌ Home thất bại")
    
    def on_jog_cw_pressed(self):
        """JOG+ pressed"""
        speed = self.spin_jog_speed.value()
        if self.driver.jog_move(speed, direction=1):
            self.log_message(f"▶️ JOG+ @ {speed} pps")
            self.lbl_motor_status.setText("🏃 JOG+")
    
    def on_jog_ccw_pressed(self):
        """JOG- pressed"""
        speed = self.spin_jog_speed.value()
        if self.driver.jog_move(speed, direction=0):
            self.log_message(f"◀️ JOG- @ {speed} pps")
            self.lbl_motor_status.setText("🏃 JOG-")
    
    def on_jog_released(self):
        """JOG released - stop"""
        if self.driver.stop():
            self.lbl_motor_status.setText("⏸ STOPPED")
            self.update_status()  # Cập nhật vị trí sau khi JOG
    
    def on_abs_move(self):
        """Absolute Move"""
        position = self.spin_cmd_pos.value()
        move_speed = self.spin_move_speed.value()  # ⚠️ Dùng tốc độ Move riêng
        if self.driver.move_absolute(position, move_speed):
            self.log_message(f"📍 ABS Move: {position} @ {move_speed} pps")
            self.lbl_motor_status.setText("🏃 MOVING")
            self.update_status()  # Cập nhật vị trí ngay
    
    def on_dec_move(self):
        """DEC Move"""
        distance = -abs(self.spin_cmd_pos.value())
        move_speed = self.spin_move_speed.value()  # ⚠️ Dùng tốc độ Move chung
        if self.driver.move_relative(distance, move_speed):
            self.log_message(f"◀️ DEC: {distance} @ {move_speed} pps")
            self.lbl_motor_status.setText("🏃 DEC")
            self.update_status()  # Cập nhật vị trí ngay
    
    def on_inc_move(self):
        """INC Move"""
        distance = abs(self.spin_cmd_pos.value())
        move_speed = self.spin_move_speed.value()  # ⚠️ Dùng tốc độ Move chung
        if self.driver.move_relative(distance, move_speed):
            self.log_message(f"▶️ INC: +{distance} @ {move_speed} pps")
            self.lbl_motor_status.setText("🏃 INC")
            self.update_status()  # Cập nhật vị trí ngay
    
    def update_status(self):
        """Cập nhật trạng thái"""
        position = self.driver.read_position()
        if position is not None:
            self.lcd_position.display(position)
    
    def log_message(self, message):
        """Ghi log"""
        self.txt_log.append(message)
        logger.info(message)
    
    def cleanup(self):
        """Cleanup khi đóng app"""
        self.status_timer.stop()
