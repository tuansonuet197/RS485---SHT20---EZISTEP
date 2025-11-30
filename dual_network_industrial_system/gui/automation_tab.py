"""
BÀI TẬP LỚN: HỆ THỐNG GIÁM SÁT VÀ ĐIỀU KHIỂN CÔNG NGHIỆP
Môn: Kiến trúc máy tính và mạng truyền thông công nghiệp
Lớp: INT 2013 44
Giảng viên: ThS. Đặng Anh Việt, ThS. Nguyễn Quang Nhã
Sinh viên: Nguyễn Tuấn Sơn (MSV: 23021335)

Module: Automation Tab - Giao diện điều khiển tự động
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
                            QTextEdit, QGridLayout, QFrame, QSplitter)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import pyqtgraph as pg
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AutomationTab(QWidget):
    """Tab hiển thị và điều khiển automation system"""
    
    def __init__(self, automation_controller, sht20_controller=None, ezistep_controller=None):
        super().__init__()
        self.automation = automation_controller
        self.sht20 = sht20_controller
        self.ezistep = ezistep_controller
        
        # Dữ liệu hiện tại
        self.current_temp = 0.0
        self.current_humid = 0.0
        self.current_motor_status = {'running': False, 'speed': 0}
        
        # Dữ liệu cho đồ thị
        self.time_data = []
        self.temp_data = []
        self.motor_status_data = []
        self.max_points = 100
        
        self.init_ui()
        self.connect_signals()
        
        # Timer để cập nhật UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(500)  # Cập nhật mỗi 0.5s
        
        # Timer để đồng bộ chế độ tự động với Thingspeak
        self.thingspeak_timer = QTimer()
        self.thingspeak_timer.timeout.connect(self.sync_automation_with_thingspeak)
        self.thingspeak_timer.start(5000)  # 5 giây/lần

        # Thông tin Thingspeak (cần sửa đúng channel_id và read_api_key)
        self.thingspeak_channel_id = 3187134  # Thay bằng channel ID của bạn
        self.thingspeak_read_api_key = 'PT2JXYRX7GFGBOBD'  # Thay bằng Read API Key của bạn
        self._last_cloud_mode = None

    def init_ui(self):
        """Khởi tạo giao diện"""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("🤖 ĐIỀU KHIỂN TỰ ĐỘNG THÔNG MINH")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Splitter chính (trên/dưới)
        splitter = QSplitter(Qt.Vertical)
        
        # ===== PHẦN TRÊN: Controls + Status =====
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        
        # Control Panel (trái)
        control_group = self.create_control_panel()
        top_layout.addWidget(control_group, 1)
        
        # Status Panel (phải)
        status_group = self.create_status_panel()
        top_layout.addWidget(status_group, 1)
        
        top_widget.setLayout(top_layout)
        splitter.addWidget(top_widget)
        
        # ===== PHẦN GIỮA: Rules Configuration =====
        rules_group = self.create_rules_panel()
        splitter.addWidget(rules_group)
        
        # ===== PHẦN DƯỚI: Chart + Activity Log =====
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()
        
        # Chart (trái)
        chart_group = self.create_chart_panel()
        bottom_layout.addWidget(chart_group, 2)
        
        # Activity Log (phải)
        log_group = self.create_log_panel()
        bottom_layout.addWidget(log_group, 1)
        
        bottom_widget.setLayout(bottom_layout)
        splitter.addWidget(bottom_widget)
        
        # Set splitter sizes
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_control_panel(self):
        """Tạo panel điều khiển automation"""
        group = QGroupBox("⚙️ ĐIỀU KHIỂN TỰ ĐỘNG")
        layout = QVBoxLayout()
        
        # Enable/Disable checkbox
        self.enable_checkbox = QCheckBox("🤖 Bật Điều Khiển Tự Động")
        self.enable_checkbox.setFont(QFont("Arial", 11, QFont.Bold))
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_checkbox)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Status indicator
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Trạng thái:"))
        self.status_label = QLabel("⚫ TẮT")
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Statistics
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Số lần kích hoạt:"), 0, 0)
        self.total_triggers_label = QLabel("0")
        self.total_triggers_label.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout.addWidget(self.total_triggers_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Quy tắc đang bật:"), 1, 0)
        self.active_rules_label = QLabel("0/0")
        self.active_rules_label.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout.addWidget(self.active_rules_label, 1, 1)
        
        layout.addLayout(stats_layout)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QVBoxLayout()
        
        self.reset_btn = QPushButton("🔄 Đặt Lại Thống Kê")
        self.reset_btn.clicked.connect(self.reset_statistics)
        btn_layout.addWidget(self.reset_btn)
        
        self.clear_log_btn = QPushButton("🗑️ Xóa Nhật Ký")
        self.clear_log_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.clear_log_btn)
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
        
    def create_status_panel(self):
        """Tạo panel hiển thị trạng thái hiện tại"""
        group = QGroupBox("📊 TRẠNG THÁI HIỆN TẠI")
        layout = QGridLayout()
        
        # Temperature
        layout.addWidget(QLabel("🌡️ Nhiệt độ:"), 0, 0)
        self.temp_value_label = QLabel("-- °C")
        self.temp_value_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.temp_value_label, 0, 1)
        self.temp_status_label = QLabel("⚪ --")
        layout.addWidget(self.temp_status_label, 0, 2)
        
        # Humidity
        layout.addWidget(QLabel("💧 Độ ẩm:"), 1, 0)
        self.humid_value_label = QLabel("-- %")
        self.humid_value_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.humid_value_label, 1, 1)
        self.humid_status_label = QLabel("⚪ --")
        layout.addWidget(self.humid_status_label, 1, 2)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 2, 0, 1, 3)
        
        # Motor Status
        layout.addWidget(QLabel("⚙️ Trạng thái động cơ:"), 3, 0)
        self.motor_status_label = QLabel("🛑 DỪNG")
        self.motor_status_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(self.motor_status_label, 3, 1, 1, 2)
        
        # Motor Speed
        layout.addWidget(QLabel("🎯 Tốc độ động cơ:"), 4, 0)
        self.motor_speed_label = QLabel("0 pps")
        self.motor_speed_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.motor_speed_label, 4, 1, 1, 2)
        
        layout.setRowStretch(5, 1)
        
        group.setLayout(layout)
        return group
        
    def create_rules_panel(self):
        """Tạo panel cấu hình rules"""
        group = QGroupBox("📋 CẤU HÌNH QUY TẮC TỰ ĐỘNG")
        layout = QVBoxLayout()
        
        # Rule 1: High Temperature
        rule1_layout = QHBoxLayout()
        self.rule1_check = QCheckBox("Quy tắc 1: Điều khiển khi nhiệt độ cao")
        self.rule1_check.setChecked(True)
        self.rule1_check.stateChanged.connect(lambda: self.toggle_rule("High Temperature Motor Start"))
        rule1_layout.addWidget(self.rule1_check)
        rule1_layout.addWidget(QLabel("Nếu Temp >"))
        self.rule1_temp = QDoubleSpinBox()
        self.rule1_temp.setRange(0.0, 80.0)
        self.rule1_temp.setValue(28.0)
        self.rule1_temp.setSuffix(" °C")
        self.rule1_temp.valueChanged.connect(lambda v: self.update_rule_param("High Temperature Motor Start", "temp_threshold", v))
        rule1_layout.addWidget(self.rule1_temp)
        rule1_layout.addWidget(QLabel("→ Bật motor CW tại"))
        self.rule1_speed = QSpinBox()
        self.rule1_speed.setRange(1000, 50000)
        self.rule1_speed.setValue(8000)
        self.rule1_speed.setSuffix(" pps")
        self.rule1_speed.valueChanged.connect(lambda v: self.update_rule_param("High Temperature Motor Start", "motor_speed", v))
        rule1_layout.addWidget(self.rule1_speed)
        rule1_layout.addStretch()
        layout.addLayout(rule1_layout)
        
        # Rule 2: Low Temperature
        rule2_layout = QHBoxLayout()
        self.rule2_check = QCheckBox("Quy tắc 2: Điều khiển khi nhiệt độ thấp")
        self.rule2_check.setChecked(True)
        self.rule2_check.stateChanged.connect(lambda: self.toggle_rule("Low Temperature Motor Stop"))
        rule2_layout.addWidget(self.rule2_check)
        rule2_layout.addWidget(QLabel("Nếu Temp <"))
        self.rule2_temp = QDoubleSpinBox()
        self.rule2_temp.setRange(0.0, 80.0)
        self.rule2_temp.setValue(26.0)
        self.rule2_temp.setSuffix(" °C")
        self.rule2_temp.valueChanged.connect(lambda v: self.update_rule_param("Low Temperature Motor Stop", "temp_threshold", v))
        rule2_layout.addWidget(self.rule2_temp)
        rule2_layout.addWidget(QLabel("→ Tắt motor"))
        rule2_layout.addStretch()
        layout.addLayout(rule2_layout)
        
        # Rule 3: High Humidity
        rule3_layout = QHBoxLayout()
        self.rule3_check = QCheckBox("Quy tắc 3: Điều khiển khi độ ẩm cao")
        self.rule3_check.setChecked(False)
        self.rule3_check.stateChanged.connect(lambda: self.toggle_rule("High Humidity Motor Stop"))
        rule3_layout.addWidget(self.rule3_check)
        rule3_layout.addWidget(QLabel("Nếu độ ẩm >"))
        self.rule3_humid = QDoubleSpinBox()
        self.rule3_humid.setRange(0.0, 100.0)
        self.rule3_humid.setValue(65.0)
        self.rule3_humid.setSuffix(" %")
        self.rule3_humid.valueChanged.connect(lambda v: self.update_rule_param("High Humidity Motor Stop", "humid_threshold", v))
        rule3_layout.addWidget(self.rule3_humid)
        rule3_layout.addWidget(QLabel("→ Tắt motor"))
        rule3_layout.addStretch()
        layout.addLayout(rule3_layout)
        
        # Rule 4: Low Humidity
        rule4_layout = QHBoxLayout()
        self.rule4_check = QCheckBox("Quy tắc 4: Điều khiển khi độ ẩm thấp")
        self.rule4_check.setChecked(False)
        self.rule4_check.stateChanged.connect(lambda: self.toggle_rule("Low Humidity Motor Start"))
        rule4_layout.addWidget(self.rule4_check)
        rule4_layout.addWidget(QLabel("Nếu độ ẩm <"))
        self.rule4_humid = QDoubleSpinBox()
        self.rule4_humid.setRange(0.0, 100.0)
        self.rule4_humid.setValue(40.0)
        self.rule4_humid.setSuffix(" %")
        self.rule4_humid.valueChanged.connect(lambda v: self.update_rule_param("Low Humidity Motor Start", "humid_threshold", v))
        rule4_layout.addWidget(self.rule4_humid)
        rule4_layout.addWidget(QLabel("→ Bật motor CW tại"))
        self.rule4_speed = QSpinBox()
        self.rule4_speed.setRange(1000, 50000)
        self.rule4_speed.setValue(5000)
        self.rule4_speed.setSuffix(" pps")
        self.rule4_speed.valueChanged.connect(lambda v: self.update_rule_param("Low Humidity Motor Start", "motor_speed", v))
        rule4_layout.addWidget(self.rule4_speed)
        rule4_layout.addStretch()
        layout.addLayout(rule4_layout)
        
        group.setLayout(layout)
        return group
        
    def create_chart_panel(self):
        """Tạo panel đồ thị real-time"""
        group = QGroupBox("📈 GIÁM SÁT THEO THỜI GIAN THỰC")
        layout = QVBoxLayout()
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', 'Nhiệt độ (°C)', color='red')
        self.plot_widget.setLabel('bottom', 'Thời gian (mẫu)', color='black')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setYRange(15, 40)
        
        # Temperature curve (red)
        self.temp_curve = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='Nhiệt độ')
        
        # Motor status (green/gray regions)
        self.motor_region = pg.LinearRegionItem([0, 0], brush=(0, 255, 0, 50), movable=False)
        self.plot_widget.addItem(self.motor_region)
        
        # Legend
        legend = self.plot_widget.addLegend()
        
        layout.addWidget(self.plot_widget)
        
        group.setLayout(layout)
        return group
        
    def create_log_panel(self):
        """Tạo panel activity log"""
        group = QGroupBox("📝 NHẬT KÝ HOẠT ĐỘNG")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        font = QFont("Consolas", 9)
        self.log_text.setFont(font)
        
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
        
    def connect_signals(self):
        """Kết nối signals từ automation controller"""
        if self.automation:
            self.automation.action_executed.connect(self.on_action_executed)
            self.automation.status_changed.connect(self.on_automation_status_changed)
            
    @pyqtSlot(int)
    def on_enable_changed(self, state):
        """Xử lý khi checkbox enable/disable thay đổi"""
        enabled = (state == Qt.Checked)
        
        # Cập nhật trạng thái automation
        self.automation.set_enabled(enabled)
        
        # Cập nhật UI ngay lập tức
        if enabled:
            self.status_label.setText("🟢 BẬT")
            self.status_label.setStyleSheet("color: green;")
            self.add_log("🤖 Đã bật điều khiển tự động")
        else:
            self.status_label.setText("⚫ TẮT")
            self.status_label.setStyleSheet("color: gray;")
            self.add_log("🤖 Đã tắt điều khiển tự động")
            
            # QUAN TRỌNG: Dừng motor khi tắt automation
            if self.ezistep and self.ezistep.is_connected and self.ezistep.is_running:
                try:
                    self.ezistep.stop()
                    self.add_log("🛑 Đã dừng motor khi tắt automation")
                except Exception as e:
                    self.add_log(f"⚠️ Lỗi khi dừng motor: {e}", color="red")
        
    @pyqtSlot(bool)
    def on_automation_status_changed(self, enabled):
        """Cập nhật UI khi automation status thay đổi"""
        if enabled:
            self.status_label.setText("🟢 BẬT")
            self.status_label.setStyleSheet("color: green;")
            self.add_log("🤖 Đã bật điều khiển tự động")
        else:
            self.status_label.setText("⚫ TẮT")
            self.status_label.setStyleSheet("color: gray;")
            self.add_log("🤖 Đã tắt điều khiển tự động")
            
    @pyqtSlot(str, str, bool)
    def on_action_executed(self, rule_name, message, success):
        """Xử lý khi rule được trigger"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            log_msg = f"[{timestamp}] ✅ {rule_name}: {message}"
            self.add_log(log_msg, color="green")
        else:
            log_msg = f"[{timestamp}] ❌ {rule_name}: {message}"
            self.add_log(log_msg, color="red")
            
    def toggle_rule(self, rule_name):
        """Bật/tắt rule"""
        rule = self.automation.get_rule_by_name(rule_name)
        if rule:
            # Toggle enabled state dựa vào checkbox tương ứng
            if "High Temperature" in rule_name:
                rule.enabled = self.rule1_check.isChecked()
            elif "Low Temperature" in rule_name:
                rule.enabled = self.rule2_check.isChecked()
            elif "High Humidity" in rule_name:
                rule.enabled = self.rule3_check.isChecked()
            elif "Low Humidity" in rule_name:
                rule.enabled = self.rule4_check.isChecked()
                
            status = "đã bật" if rule.enabled else "đã tắt"
            self.add_log(f"Quy tắc '{rule_name}' {status}")
            
    def update_rule_param(self, rule_name, param_name, value):
        """Cập nhật parameter của rule"""
        success = self.automation.update_rule_threshold(rule_name, param_name, value)
        if success:
            # Hiển thị giá trị dễ đọc
            if param_name == "motor_speed":
                display_value = f"{value} pps"
            elif "temp" in param_name:
                display_value = f"{value} °C"
            elif "humid" in param_name:
                display_value = f"{value} %"
            else:
                display_value = str(value)
            self.add_log(f"⚙️ Cập nhật '{rule_name}': {param_name} = {display_value}")
        else:
            self.add_log(f"⚠️ Không thể cập nhật '{rule_name}': {param_name}", color="orange")
            
    def update_sensor_data(self, temperature, humidity):
        """Cập nhật dữ liệu từ SHT20"""
        self.current_temp = temperature
        self.current_humid = humidity
        
        # Cập nhật motor status từ ezistep controller
        if self.ezistep and self.ezistep.is_connected:
            self.current_motor_status = {
                'running': self.ezistep.is_running,
                'speed': self.ezistep.current_speed
            }
        else:
            self.current_motor_status = {
                'running': False,
                'speed': 0
            }
            
        # Gửi dữ liệu cho automation controller
        self.automation.process_sensor_data(
            self.current_temp,
            self.current_humid,
            self.current_motor_status
        )
        
        # Cập nhật chart data
        current_time = len(self.time_data)
        self.time_data.append(current_time)
        self.temp_data.append(temperature)
        self.motor_status_data.append(1 if self.current_motor_status['running'] else 0)
        
        # Giới hạn số điểm
        if len(self.time_data) > self.max_points:
            self.time_data.pop(0)
            self.temp_data.pop(0)
            self.motor_status_data.pop(0)
            
    def update_ui(self):
        """Cập nhật UI định kỳ"""
        # Update current status
        self.temp_value_label.setText(f"{self.current_temp:.1f} °C")
        self.humid_value_label.setText(f"{self.current_humid:.1f} %")
        
        # Temperature status
        if self.current_temp > self.rule1_temp.value():
            self.temp_status_label.setText("🔴 CAO")
            self.temp_status_label.setStyleSheet("color: red;")
        elif self.current_temp < self.rule2_temp.value():
            self.temp_status_label.setText("🔵 THẤP")
            self.temp_status_label.setStyleSheet("color: blue;")
        else:
            self.temp_status_label.setText("🟢 Bình thường")
            self.temp_status_label.setStyleSheet("color: green;")
            
        # Humidity status
        if self.current_humid > self.rule3_humid.value():
            self.humid_status_label.setText("🔴 CAO")
            self.humid_status_label.setStyleSheet("color: red;")
        elif self.current_humid < self.rule4_humid.value():
            self.humid_status_label.setText("🔵 THẤP")
            self.humid_status_label.setStyleSheet("color: blue;")
        else:
            self.humid_status_label.setText("🟢 Bình thường")
            self.humid_status_label.setStyleSheet("color: green;")
            
        # Motor status
        if self.current_motor_status['running']:
            self.motor_status_label.setText("🔄 ĐANG CHẠY (TỰ ĐỘNG)")
            self.motor_status_label.setStyleSheet("color: green;")
            self.motor_speed_label.setText(f"{self.current_motor_status['speed']} pps")
        else:
            self.motor_status_label.setText("🛑 DỪNG")
            self.motor_status_label.setStyleSheet("color: gray;")
            self.motor_speed_label.setText("0 pps")
            
        # Update statistics
        stats = self.automation.get_statistics()
        self.total_triggers_label.setText(str(stats['total_triggers']))
        self.active_rules_label.setText(f"{stats['active_rules']}/{stats['total_rules']}")
        
        # Update chart
        if len(self.time_data) > 0:
            self.temp_curve.setData(self.time_data, self.temp_data)
            
            # Update motor region (highlight when motor running)
            # Find continuous running segments
            # (Simplified: just show if currently running)
            if self.current_motor_status['running'] and len(self.time_data) > 1:
                self.motor_region.setRegion([self.time_data[-10] if len(self.time_data) > 10 else self.time_data[0], 
                                             self.time_data[-1]])
            
    def add_log(self, message, color=None):
        """Thêm message vào activity log"""
        if color:
            message = f'<span style="color: {color};">{message}</span>'
        self.log_text.append(message)
        # Auto scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
    def reset_statistics(self):
        """Reset statistics"""
        self.automation.total_triggers = 0
        for rule in self.automation.rules:
            rule.trigger_count = 0
            rule.last_trigger_time = None
        self.add_log("📊 Đã đặt lại thống kê")
        
    def clear_log(self):
        """Xóa activity log"""
        self.log_text.clear()
        self.add_log("Đã xóa nhật ký hoạt động")
    
    def cleanup(self):
        """Cleanup khi đóng tab - Dừng motor nếu đang chạy"""
        # Tắt automation trước
        if self.automation.enabled:
            self.automation.set_enabled(False)
        
        # Dừng motor nếu đang chạy
        if self.ezistep and self.ezistep.is_connected and self.ezistep.is_running:
            try:
                self.ezistep.stop()
                logger.info("🛑 Automation cleanup: Motor stopped")
            except Exception as e:
                logger.error(f"Error stopping motor in cleanup: {e}")
                
    def sync_automation_with_thingspeak(self):
        """Đồng bộ trạng thái automation với Thingspeak field3"""
        import requests
        url = f'https://api.thingspeak.com/channels/{self.thingspeak_channel_id}/fields/3/last.json?api_key={self.thingspeak_read_api_key}'
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                value = data.get('field3')
                if value is not None:
                    try:
                        mode = int(value)
                    except Exception:
                        return
                    # Nếu trạng thái cloud khác trạng thái hiện tại thì cập nhật
                    if mode != self._last_cloud_mode:
                        self._last_cloud_mode = mode
                        # Cập nhật checkbox (nếu khác)
                        checked = (mode == 1)
                        if self.enable_checkbox.isChecked() != checked:
                            self.enable_checkbox.blockSignals(True)
                            self.enable_checkbox.setChecked(checked)
                            self.enable_checkbox.blockSignals(False)
                            # Gọi xử lý bật/tắt automation
                            self.on_enable_changed(Qt.Checked if checked else Qt.Unchecked)
        except Exception as e:
            logger.warning(f"Lỗi đồng bộ automation với Thingspeak: {e}")
