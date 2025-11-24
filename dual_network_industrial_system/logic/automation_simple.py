"""
BÀI TẬP LỚN: HỆ THỐNG GIÁM SÁT VÀ ĐIỀU KHIỂN CÔNG NGHIỆP
Môn: Kiến trúc máy tính và mạng truyền thông công nghiệp
Lớp: INT 2013 44
Giảng viên: ThS. Đặng Anh Việt, ThS. Nguyễn Quang Nhã
Sinh viên: Nguyễn Tuấn Sơn (MSV: 23021335)

Module: Automation Logic - Điều khiển tự động dựa trên nhiệt độ/độ ẩm
"""

from PyQt5.QtCore import QObject, pyqtSignal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AutomationRule:
    """Định nghĩa một rule tự động"""
    
    def __init__(self, name, description, enabled=True):
        self.name = name
        self.description = description
        self.enabled = enabled
        self.last_trigger_time = None
        self.trigger_count = 0
        
    def check_condition(self, temperature, humidity, motor_status):
        """Override method này trong subclass"""
        raise NotImplementedError
        
    def execute_action(self):
        """Override method này trong subclass"""
        raise NotImplementedError


class HighTempMotorStartRule(AutomationRule):
    """Rule: Nhiệt độ cao → Bật motor"""
    
    def __init__(self, temp_threshold=28.0, motor_speed=8000):
        super().__init__(
            name="High Temperature Motor Start",
            description=f"IF Temp > {temp_threshold}°C → Motor CW at {motor_speed}pps"
        )
        self.temp_threshold = temp_threshold
        self.motor_speed = motor_speed
        self.motor_controller = None
        
    def check_condition(self, temperature, humidity, motor_status):
        """Kiểm tra: nhiệt độ > ngưỡng VÀ motor chưa chạy"""
        return (temperature > self.temp_threshold and 
                motor_status.get('running', False) == False)
                
    def execute_action(self):
        """Thực hiện: Bật motor CW"""
        if self.motor_controller:
            try:
                self.motor_controller.jog_move(self.motor_speed, direction=1)  # CW direction
                self.trigger_count += 1
                self.last_trigger_time = datetime.now()
                return True, f"Motor started CW at {self.motor_speed}pps"
            except Exception as e:
                return False, f"Failed to start motor: {str(e)}"
        return False, "Motor controller not set"


class LowTempMotorStopRule(AutomationRule):
    """Rule: Nhiệt độ thấp → Tắt motor"""
    
    def __init__(self, temp_threshold=26.0):
        super().__init__(
            name="Low Temperature Motor Stop",
            description=f"IF Temp < {temp_threshold}°C → Motor STOP"
        )
        self.temp_threshold = temp_threshold
        self.motor_controller = None
        
    def check_condition(self, temperature, humidity, motor_status):
        """Kiểm tra: nhiệt độ < ngưỡng VÀ motor đang chạy"""
        return (temperature < self.temp_threshold and 
                motor_status.get('running', False) == True)
                
    def execute_action(self):
        """Thực hiện: Dừng motor"""
        if self.motor_controller:
            try:
                self.motor_controller.stop()
                self.trigger_count += 1
                self.last_trigger_time = datetime.now()
                return True, "Motor stopped"
            except Exception as e:
                return False, f"Failed to stop motor: {str(e)}"
        return False, "Motor controller not set"


class HighHumidityMotorStopRule(AutomationRule):
    """Rule: Độ ẩm cao → Tắt motor (tắt máy phun sương)"""
    
    def __init__(self, humid_threshold=65.0):
        super().__init__(
            name="High Humidity Motor Stop",
            description=f"IF Humidity > {humid_threshold}% → Motor STOP",
            enabled=False  # Mặc định tắt
        )
        self.humid_threshold = humid_threshold
        self.motor_controller = None
        
    def check_condition(self, temperature, humidity, motor_status):
        """Kiểm tra: độ ẩm > ngưỡng VÀ motor đang chạy"""
        return (humidity > self.humid_threshold and 
                motor_status.get('running', False) == True)
                
    def execute_action(self):
        """Thực hiện: Dừng motor"""
        if self.motor_controller:
            try:
                self.motor_controller.stop()
                self.trigger_count += 1
                self.last_trigger_time = datetime.now()
                return True, "Motor stopped (high humidity)"
            except Exception as e:
                return False, f"Failed to stop motor: {str(e)}"
        return False, "Motor controller not set"


class LowHumidityMotorStartRule(AutomationRule):
    """Rule: Độ ẩm thấp → Bật motor (bật máy phun sương)"""
    
    def __init__(self, humid_threshold=40.0, motor_speed=5000):
        super().__init__(
            name="Low Humidity Motor Start",
            description=f"IF Humidity < {humid_threshold}% → Motor CW at {motor_speed}pps",
            enabled=False  # Mặc định tắt
        )
        self.humid_threshold = humid_threshold
        self.motor_speed = motor_speed
        self.motor_controller = None
        
    def check_condition(self, temperature, humidity, motor_status):
        """Kiểm tra: độ ẩm < ngưỡng VÀ motor chưa chạy"""
        return (humidity < self.humid_threshold and 
                motor_status.get('running', False) == False)
                
    def execute_action(self):
        """Thực hiện: Bật motor CW"""
        if self.motor_controller:
            try:
                self.motor_controller.jog_move(self.motor_speed, direction=1)  # CW direction
                self.trigger_count += 1
                self.last_trigger_time = datetime.now()
                return True, f"Motor started CW at {self.motor_speed}pps (low humidity)"
            except Exception as e:
                return False, f"Failed to start motor: {str(e)}"
        return False, "Motor controller not set"


class AutomationController(QObject):
    """
    Controller chính cho automation system
    Xử lý tất cả các rules và gửi signal khi có action
    """
    
    # Signals
    action_executed = pyqtSignal(str, str, bool)  # (rule_name, message, success)
    status_changed = pyqtSignal(bool)  # (enabled/disabled)
    
    def __init__(self, motor_controller=None):
        super().__init__()
        self.motor_controller = motor_controller
        self.enabled = False
        
        # Khởi tạo các rules
        self.rules = [
            HighTempMotorStartRule(temp_threshold=28.0, motor_speed=8000),
            LowTempMotorStopRule(temp_threshold=26.0),
            HighHumidityMotorStopRule(humid_threshold=65.0),
            LowHumidityMotorStartRule(humid_threshold=40.0, motor_speed=5000)
        ]
        
        # Set motor controller cho tất cả rules
        for rule in self.rules:
            rule.motor_controller = motor_controller
            
        # Statistics
        self.total_triggers = 0
        self.last_check_time = None
        
        logger.info("Automation Controller initialized with %d rules", len(self.rules))
        
    def set_motor_controller(self, motor_controller):
        """Cập nhật motor controller cho tất cả rules"""
        self.motor_controller = motor_controller
        for rule in self.rules:
            rule.motor_controller = motor_controller
        logger.info("Motor controller updated for automation")
        
    def set_enabled(self, enabled):
        """Bật/tắt automation"""
        self.enabled = enabled
        self.status_changed.emit(enabled)
        if enabled:
            logger.info("🤖 Automation ENABLED")
        else:
            logger.info("🤖 Automation DISABLED")
            
    def process_sensor_data(self, temperature, humidity, motor_status):
        """
        Xử lý dữ liệu từ sensor và kiểm tra tất cả rules
        
        Args:
            temperature: Nhiệt độ hiện tại (°C)
            humidity: Độ ẩm hiện tại (%)
            motor_status: Dict chứa trạng thái motor {'running': bool, 'speed': int, ...}
        """
        if not self.enabled:
            return
            
        self.last_check_time = datetime.now()
        
        # Kiểm tra từng rule
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            try:
                # Kiểm tra điều kiện
                if rule.check_condition(temperature, humidity, motor_status):
                    # Thực hiện action
                    success, message = rule.execute_action()
                    
                    if success:
                        self.total_triggers += 1
                        log_message = (f"🤖 AUTO [{rule.name}]: "
                                     f"Temp={temperature:.1f}°C, "
                                     f"Humid={humidity:.1f}% → {message}")
                        logger.info(log_message)
                        self.action_executed.emit(rule.name, message, True)
                    else:
                        logger.error(f"Rule '{rule.name}' failed: {message}")
                        self.action_executed.emit(rule.name, message, False)
                        
            except Exception as e:
                error_msg = f"Error processing rule '{rule.name}': {str(e)}"
                logger.error(error_msg)
                self.action_executed.emit(rule.name, error_msg, False)
                
    def get_rule_by_name(self, name):
        """Lấy rule theo tên"""
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
        
    def update_rule_threshold(self, rule_name, param_name, value):
        """Cập nhật ngưỡng của rule"""
        rule = self.get_rule_by_name(rule_name)
        if rule:
            if hasattr(rule, param_name):
                old_value = getattr(rule, param_name)
                setattr(rule, param_name, value)
                logger.info(f"✅ Rule '{rule_name}': {param_name} changed {old_value} → {value}")
                return True
            else:
                logger.warning(f"⚠️ Rule '{rule_name}' doesn't have attribute '{param_name}'")
                return False
        else:
            logger.warning(f"⚠️ Rule '{rule_name}' not found")
            return False
        
    def get_statistics(self):
        """Lấy thống kê automation"""
        return {
            'enabled': self.enabled,
            'total_rules': len(self.rules),
            'active_rules': sum(1 for r in self.rules if r.enabled),
            'total_triggers': self.total_triggers,
            'last_check': self.last_check_time,
            'rules_status': [
                {
                    'name': rule.name,
                    'enabled': rule.enabled,
                    'triggers': rule.trigger_count,
                    'last_trigger': rule.last_trigger_time
                }
                for rule in self.rules
            ]
        }
