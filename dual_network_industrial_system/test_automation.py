"""
BÀI TẬP LỚN: HỆ THỐNG GIÁM SÁT VÀ ĐIỀU KHIỂN CÔNG NGHIỆP
Script test nhanh tính năng Automation

Test automation logic đơn giản mà không cần phần cứng
"""

import sys
import time
from logic.automation_simple import AutomationController, HighTempMotorStartRule, LowTempMotorStopRule

# Mock motor controller để test
class MockMotorController:
    def __init__(self):
        self.is_running = False
        self.current_speed = 0
        self.direction = None
        
    def jog_move(self, direction, speed):
        print(f"  🔄 Motor started: {direction} @ {speed} pps")
        self.is_running = True
        self.current_speed = speed
        self.direction = direction
        
    def stop(self):
        print(f"  🛑 Motor stopped")
        self.is_running = False
        self.current_speed = 0
        self.direction = None
        
    def get_status(self):
        return {
            'running': self.is_running,
            'speed': self.current_speed,
            'direction': self.direction
        }


def test_automation():
    """Test automation với dữ liệu giả lập"""
    
    print("=" * 60)
    print("TEST AUTOMATION SYSTEM")
    print("=" * 60)
    
    # Tạo mock motor controller
    motor = MockMotorController()
    
    # Tạo automation controller
    automation = AutomationController(motor_controller=motor)
    
    # Enable automation
    automation.set_enabled(True)
    print("\n✅ Automation enabled\n")
    
    # Test scenarios
    scenarios = [
        # (temperature, humidity, description)
        (25.0, 50.0, "Trạng thái bình thường"),
        (27.0, 52.0, "Nhiệt độ tăng nhẹ"),
        (28.5, 54.0, "🔥 Nhiệt độ cao (Rule 1 trigger)"),
        (29.0, 55.0, "Nhiệt độ vẫn cao (motor đang chạy)"),
        (27.5, 53.0, "Nhiệt độ giảm nhẹ"),
        (25.5, 51.0, "❄️ Nhiệt độ thấp (Rule 2 trigger)"),
        (24.0, 50.0, "Nhiệt độ vẫn thấp (motor đã dừng)"),
    ]
    
    print("\n" + "=" * 60)
    print("SIMULATION START")
    print("=" * 60 + "\n")
    
    for i, (temp, humid, description) in enumerate(scenarios, 1):
        print(f"[Scenario {i}] {description}")
        print(f"  📊 Temp: {temp:.1f}°C | Humidity: {humid:.1f}%")
        
        # Lấy motor status
        motor_status = motor.get_status()
        print(f"  ⚙️ Motor before: {'RUNNING' if motor_status['running'] else 'STOPPED'}")
        
        # Process data
        automation.process_sensor_data(temp, humid, motor_status)
        
        # Hiển thị motor status sau khi xử lý
        motor_status_after = motor.get_status()
        print(f"  ⚙️ Motor after: {'RUNNING' if motor_status_after['running'] else 'STOPPED'}")
        
        print()
        time.sleep(1)  # Delay để dễ theo dõi
    
    # Statistics
    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    stats = automation.get_statistics()
    print(f"Total triggers: {stats['total_triggers']}")
    print(f"Active rules: {stats['active_rules']}/{stats['total_rules']}")
    print("\nRules detail:")
    for rule_stat in stats['rules_status']:
        status = "✅ ON" if rule_stat['enabled'] else "⚫ OFF"
        print(f"  {status} {rule_stat['name']}: {rule_stat['triggers']} triggers")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


def test_individual_rules():
    """Test từng rule riêng lẻ"""
    
    print("\n" + "=" * 60)
    print("TEST INDIVIDUAL RULES")
    print("=" * 60)
    
    motor = MockMotorController()
    
    # Test Rule 1: High Temperature
    print("\n[TEST] Rule 1: High Temperature Motor Start")
    rule1 = HighTempMotorStartRule(temp_threshold=28.0, motor_speed=8000)
    rule1.motor_controller = motor
    
    print("  Condition: Temp=29.0°C (> 28.0°C), Motor=STOPPED")
    condition = rule1.check_condition(29.0, 50.0, {'running': False})
    print(f"  Check result: {condition}")
    
    if condition:
        success, msg = rule1.execute_action()
        print(f"  Execute result: {success} - {msg}")
    
    # Test Rule 2: Low Temperature
    print("\n[TEST] Rule 2: Low Temperature Motor Stop")
    rule2 = LowTempMotorStopRule(temp_threshold=26.0)
    rule2.motor_controller = motor
    
    print("  Condition: Temp=25.0°C (< 26.0°C), Motor=RUNNING")
    condition = rule2.check_condition(25.0, 50.0, {'running': True})
    print(f"  Check result: {condition}")
    
    if condition:
        success, msg = rule2.execute_action()
        print(f"  Execute result: {success} - {msg}")


if __name__ == "__main__":
    try:
        # Test automation system
        test_automation()
        
        # Test individual rules
        test_individual_rules()
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
