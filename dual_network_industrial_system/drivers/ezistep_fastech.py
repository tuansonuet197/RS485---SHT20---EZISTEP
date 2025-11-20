"""
Driver cho Bộ điều khiển động cơ Ezi-STEP Plus-R - Giao thức FASTECH
Hỗ trợ điều khiển động cơ bước qua RS485 tốc độ cao
"""
import logging
import serial
import struct
import time
from typing import Optional, List
from enum import IntEnum

logger = logging.getLogger(__name__)


class FastechCommand(IntEnum):
    """Mã lệnh FASTECH Protocol"""
    JOG_MOVE = 0x37
    MOVE_ABSOLUTE = 0x38
    MOVE_RELATIVE = 0x39
    STOP = 0x31
    SERVO_ON = 0x83
    SERVO_OFF = 0x84
    HOMING = 0x23
    READ_POSITION = 0x0C
    READ_STATUS = 0x0D
    SET_SPEED = 0x57
    ALARM_RESET = 0x04  # Reset alarm/error
    SET_POSITION = 0x24  # Set current position (giả lập đã home)
    CLEAR_POSITION = 0x20  # Clear position counter
    TEACHING_MODE = 0xA0  # Bật teaching mode (bỏ qua homing)
    WRITE_PARAM = 0x58   # Write parameter to EEPROM
    READ_PARAM = 0x52    # Read parameter from EEPROM


class MotorStatus(IntEnum):
    """Trạng thái động cơ"""
    IDLE = 0
    MOVING = 1
    HOMING = 2
    ERROR = 3
    SERVO_OFF = 4


class EziStepFastechDriver:
    """Driver điều khiển Ezi-STEP Plus-R qua FASTECH Protocol"""
    
    def __init__(self, config: dict):
        """
        Khởi tạo driver Ezi-STEP
        
        Args:
            config: Dictionary chứa cấu hình (EZISTEP_CONFIG)
        """
        self.config = config
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self._current_position = 0
        self._current_status = MotorStatus.IDLE
        
        logger.info("Ezi-STEP Driver initialized")
    
    def connect(self) -> bool:
        """
        Kết nối tới bộ điều khiển Ezi-STEP
        
        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            self.serial_port = serial.Serial(
                port=self.config['port'],
                baudrate=self.config['baudrate'],
                bytesize=self.config['data_bits'],
                stopbits=self.config['stop_bits'],
                parity=self.config['parity'],
                timeout=self.config['timeout']
            )
            
            if self.serial_port.is_open:
                self.is_connected = True
                logger.info(f"Đã kết nối Ezi-STEP trên {self.config['port']} @ {self.config['baudrate']} bps")
                
                # Test đọc trạng thái
                time.sleep(0.1)  # Đợi driver ổn định
                status = self.read_status()
                if status is not None:
                    logger.info(f"Test đọc trạng thái thành công: {status}")
                    return True
                else:
                    logger.warning("Kết nối được nhưng không đọc được trạng thái")
                    return True  # Vẫn coi là kết nối OK
            else:
                logger.error(f"Không thể mở cổng {self.config['port']}")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Lỗi Serial khi kết nối Ezi-STEP: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Lỗi không xác định khi kết nối: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Ngắt kết nối khỏi bộ điều khiển"""
        if self.serial_port and self.serial_port.is_open:
            # Tắt servo trước khi ngắt kết nối
            self.servo_off()
            time.sleep(0.1)
            
            self.serial_port.close()
            self.is_connected = False
            logger.info("Đã ngắt kết nối Ezi-STEP")
    
    def _calculate_crc(self, data: List[int]) -> int:
        """
        Tính CRC-16 cho gói tin FASTECH
        
        Args:
            data: Danh sách byte cần tính CRC
            
        Returns:
            int: Giá trị CRC 16-bit
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _build_packet(self, frame_type: int, data: List[int] = None) -> bytes:
        """
        Xây dựng gói tin FASTECH Protocol
        
        Args:
            frame_type: Mã lệnh (Command code)
            data: Dữ liệu lệnh (nếu có)
            
        Returns:
            bytes: Gói tin hoàn chỉnh
        """
        if data is None:
            data = []
        
        # Header
        packet = list(self.config['protocol']['header'])
        
        # Slave ID
        packet.append(self.config['slave_id'])
        
        # Frame Type
        packet.append(frame_type)
        
        # Data Length
        data_len = len(data)
        packet.append(data_len)
        
        # Data
        packet.extend(data)
        
        # CRC (2 bytes)
        crc = self._calculate_crc(packet[2:])  # CRC từ Slave ID đến Data
        packet.append(crc & 0xFF)        # CRC Low
        packet.append((crc >> 8) & 0xFF) # CRC High
        
        # Tail
        packet.extend(self.config['protocol']['tail'])
        
        return bytes(packet)
    
    def _decode_status_byte(self, status_byte: int) -> str:
        """Decode status byte từ phản hồi Ezi-STEP"""
        status_bits = []
        if status_byte & 0x80:
            status_bits.append("📍ACK")
        if status_byte & 0x02:
            status_bits.append("❌ALARM")
        
        return f"0x{status_byte:02X}[{' '.join(status_bits) if status_bits else 'OK'}]"
    
    def _send_command(self, frame_type: int, data: List[int] = None) -> Optional[bytes]:
        """
        Gửi lệnh và nhận phản hồi
        
        Args:
            frame_type: Mã lệnh
            data: Dữ liệu lệnh
            
        Returns:
            bytes: Phản hồi từ driver hoặc None nếu lỗi
        """
        if not self.is_connected or not self.serial_port:
            logger.warning("Chưa kết nối tới Ezi-STEP")
            return None
        
        try:
            # Xây dựng và gửi gói tin
            packet = self._build_packet(frame_type, data)
            logger.debug(f"Gửi gói tin (Frame: 0x{frame_type:02X}): {packet.hex().upper()}")
            self.serial_port.write(packet)
            
            # Đợi phản hồi
            time.sleep(0.1)  # Tăng delay lên 100ms
            
            # Đọc phản hồi (tối đa 256 bytes)
            if self.serial_port.in_waiting > 0:
                response = self.serial_port.read(self.serial_port.in_waiting)
                logger.debug(f"Nhận phản hồi ({len(response)} bytes): {response.hex().upper()}")
                
                # Decode status byte
                if len(response) >= 6:
                    status_byte = response[5]
                    logger.info(f"   ↳ Status: {self._decode_status_byte(status_byte)}")
                
                return response
            else:
                logger.warning(f"Không nhận được phản hồi cho lệnh 0x{frame_type:02X}")
                return None
                
        except serial.SerialException as e:
            logger.error(f"Lỗi Serial khi gửi lệnh: {e}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi gửi lệnh: {e}")
            return None
    
    def disable_homing_check(self) -> bool:
        """
        TẮT CHẾ ĐỘ YÊU CẦU HOMING (cho driver không có home sensor)
        Thiết lập parameter để driver chấp nhận lệnh move mà không cần homing
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("🔧 Đang TẮT yêu cầu homing...")
        
        # Parameter 0x20 (Homing Complete Flag) = 1 (giả lập đã homing)
        # Format: [Param_Addr(2 bytes), Value(4 bytes)]
        param_addr = 0x20  # Homing complete flag
        value = 1  # Set = 1 để báo đã homing
        
        data = []
        data.extend(list(struct.pack('<H', param_addr)))  # 2 bytes address
        data.extend(list(struct.pack('<I', value)))       # 4 bytes value
        
        response = self._send_command(FastechCommand.WRITE_PARAM, data)
        time.sleep(0.3)
        
        if response:
            logger.info("✅ Đã TẮT yêu cầu homing - Motor có thể move ngay!")
            return True
        else:
            logger.warning("⚠️ Không tắt được yêu cầu homing")
            return False
    
    def clear_position(self) -> bool:
        """
        Clear position counter về 0 (BỎ QUA HOMING!)
        Đây là cách chính thức để không cần home sensor
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("🔄 CLEAR POSITION COUNTER - BỎ QUA HOMING...")
        response = self._send_command(FastechCommand.CLEAR_POSITION)
        time.sleep(0.3)
        
        if response:
            logger.info("✅ Position cleared - Motor sẵn sàng di chuyển!")
            return True
        else:
            logger.warning("⚠️ Clear position không phản hồi")
            return False
    
    def enable_teaching_mode(self) -> bool:
        """
        Bật teaching mode (mode di chuyển tự do không cần homing)
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("🎓 BẬT TEACHING MODE...")
        response = self._send_command(FastechCommand.TEACHING_MODE, [0x01])
        time.sleep(0.2)
        
        if response:
            logger.info("✅ Teaching mode ON - có thể di chuyển tự do!")
            return True
        else:
            logger.warning("⚠️ Teaching mode không phản hồi")
            return False
    
    def set_position(self, position: int = 0) -> bool:
        """
        Thiết lập vị trí hiện tại (giả lập đã home)
        Dùng khi không có home sensor
        
        Args:
            position: Vị trí muốn set (mặc định 0)
            
        Returns:
            bool: True nếu thành công
        """
        logger.info(f"📍 Đang set position = {position} (giả lập HOME)...")
        data = list(struct.pack('<i', position))  # 4 bytes signed int
        response = self._send_command(FastechCommand.SET_POSITION, data)
        time.sleep(0.2)
        
        if response:
            logger.info("✅ Set position thành công - Motor đã 'HOME'!")
            return True
        else:
            logger.warning("⚠️ Set position không phản hồi")
            return False
    
    def alarm_reset(self) -> bool:
        """
        Reset ALARM/ERROR state
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("🔧 Đang reset ALARM...")
        response = self._send_command(FastechCommand.ALARM_RESET)
        time.sleep(0.2)  # Đợi device xử lý
        
        if response:
            logger.info("✅ ALARM RESET thành công")
            return True
        else:
            logger.warning("⚠️ ALARM RESET không phản hồi")
            return False
    
    def set_speed_params(self, speed: int = 5000, accel: int = 10000) -> bool:
        """
        Thiết lập vận tốc và gia tốc mặc định
        
        Args:
            speed: Tốc độ (pps)
            accel: Gia tốc (pps/s)
            
        Returns:
            bool: True nếu thành công
        """
        logger.info(f"⚙️ Đang thiết lập tốc độ: {speed} pps, gia tốc: {accel}")
        # Command 0x57: Set Speed/Accel (8 bytes: 4 speed + 4 accel)
        data = []
        data.extend(list(struct.pack('<I', speed)))   # 4 bytes speed
        data.extend(list(struct.pack('<I', accel)))   # 4 bytes accel
        
        response = self._send_command(FastechCommand.SET_SPEED, data)
        time.sleep(0.1)
        
        if response:
            logger.info("✅ Thiết lập tốc độ thành công")
            return True
        else:
            logger.warning("⚠️ Thiết lập tốc độ không phản hồi")
            return False
    
    def servo_on(self) -> bool:
        """
        Bật Servo với đầy đủ khởi tạo (ALARM RESET + SET SPEED)
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("=" * 50)
        logger.info("🚀 BẮT ĐẦU QUY TRÌNH SERVO ON")
        logger.info("=" * 50)
        
        # Bước 0: TẮT yêu cầu homing (quan trọng nhất!)
        logger.info("📍 Bước 0: Tắt yêu cầu homing...")
        self.disable_homing_check()
        time.sleep(0.3)
        
        # Bước 1: Reset ALARM nếu có
        logger.info("📍 Bước 1: Reset ALARM...")
        self.alarm_reset()
        time.sleep(0.3)
        
        # Bước 2: Bật SERVO
        logger.info("📍 Bước 2: Bật SERVO...")
        response = self._send_command(FastechCommand.SERVO_ON)
        if not response:
            logger.error("❌ SERVO ON thất bại - không nhận phản hồi")
            return False
        
        time.sleep(0.3)
        logger.info("✅ SERVO đã BẬT")
        
        # Bước 3: Thiết lập tốc độ/gia tốc
        logger.info("📍 Bước 3: Thiết lập tốc độ/gia tốc...")
        self.set_speed_params(speed=5000, accel=10000)
        time.sleep(0.2)
        
        # Bước 4: THỬ CÁC CÁCH BỎ QUA HOMING
        logger.info("📍 Bước 4: BỎ QUA HOMING - THỬ CÁC PHƯƠNG ÁN...")
        logger.warning("⚠️ Driver yêu cầu homing nhưng không có sensor!")
        
        # Phương án 1: Teaching mode
        logger.info("   → Phương án 1: Bật Teaching Mode...")
        self.enable_teaching_mode()
        time.sleep(0.2)
        
        # Phương án 2: Clear position counter
        logger.info("   → Phương án 2: Clear Position Counter...")
        self.clear_position()
        time.sleep(0.2)
        
        # Phương án 3: Set position = 0
        logger.info("   → Phương án 3: Set Position = 0...")
        self.set_position(0)
        time.sleep(0.3)
        
        self._current_status = MotorStatus.IDLE
        logger.info("=" * 50)
        logger.info("✅ SERVO ON HOÀN TẤT - SẴN SÀNG DI CHUYỂN!")
        logger.info("=" * 50)
        return True
    
    def servo_off(self) -> bool:
        """
        Tắt Servo (Disable động cơ)
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("Tắt Servo...")
        response = self._send_command(FastechCommand.SERVO_OFF)
        
        if response:
            logger.info("Servo đã tắt")
            self._current_status = MotorStatus.SERVO_OFF
            return True
        else:
            logger.error("Không thể tắt Servo")
            return False
    
    def stop(self) -> bool:
        """
        Dừng động cơ ngay lập tức
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("Dừng động cơ...")
        response = self._send_command(FastechCommand.STOP)
        
        if response:
            logger.info("Động cơ đã dừng")
            self._current_status = MotorStatus.IDLE
            return True
        else:
            logger.error("Không thể dừng động cơ")
            return False
    
    def jog_move(self, speed: int, direction: int = 1) -> bool:
        """
        Di chuyển Jog (chạy liên tục)
        
        Args:
            speed: Tốc độ (pps - pulses per second) - khuyến nghị 2000-5000 pps
            direction: Hướng (1 = CW, 0 = CCW)
            
        Returns:
            bool: True nếu thành công
        """
        # Gửi lệnh STOP trước để clear trạng thái cũ
        logger.info("📍 Gửi STOP để clear trạng thái...")
        self._send_command(FastechCommand.STOP)
        time.sleep(0.1)
        
        # Tăng tốc độ tối thiểu lên 5000 pps để đảm bảo động cơ quay
        if speed < 5000:
            logger.warning(f"⚠️ Tốc độ {speed} pps quá thấp! Tự động tăng lên 5000 pps")
            speed = 5000
        
        logger.info(f"🏃 JOG {'CW ➡️' if direction > 0 else 'CCW ⬅️'} @ {speed} pps")
        
        # Kiểm tra tốc độ
        max_speed = self.config['motor']['max_speed'] * self.config['motor']['resolution'] / 60
        if speed > max_speed:
            logger.warning(f"Tốc độ {speed} vượt quá giới hạn {max_speed}")
            speed = int(max_speed)
        
        # Format JOG theo Ezi-STEP datasheet:
        # Data có thể cần: Speed(4) + Accel(4) + Decel(4) + Direction(1) = 13 bytes
        # HOẶC chỉ cần: Speed(4) + Direction(1) = 5 bytes
        
        # THỬ NGHIỆM 1: Chỉ speed + direction (format đơn giản)
        data = []
        data.extend(list(struct.pack('<I', abs(speed))))  # 4 bytes speed (little-endian)
        data.append(1 if direction > 0 else 0)  # 1 byte direction (1=CW, 0=CCW)
        
        logger.info(f"📦 Data format: Speed={speed} (0x{speed:08X}), Dir={'CW(1)' if direction > 0 else 'CCW(0)'}")
        
        logger.info(f"📤 Gửi JOG: Speed={speed} pps, Direction={'CW' if direction > 0 else 'CCW'}")
        logger.debug(f"   Data bytes: {[hex(x) for x in data]}")
        
        # THỬ NGHIỆM: Dùng JOG command
        response = self._send_command(FastechCommand.JOG_MOVE, data)
        
        if response and len(response) >= 6:
            status_byte = response[5]
            # Kiểm tra ALARM bit
            if status_byte & 0x02:
                logger.error("❌ JOG COMMAND KHÔNG SUPPORTED! Thử dùng MOVE RELATIVE thay thế...")
                # Giả lập JOG bằng Move Relative với khoảng cách rất lớn
                logger.info("🔄 Chuyển sang MOVE RELATIVE mode (giả lập JOG)...")
                distance = 1000000 if direction > 0 else -1000000  # 1 triệu pulse
                return self.move_relative(distance, speed)
            
            self._current_status = MotorStatus.MOVING
            logger.info("✅ Lệnh Jog đã được chấp nhận - ĐỘNG CƠ NÊN QUAY!")
            return True
        else:
            logger.error("❌ Driver không chấp nhận lệnh Jog hoặc không phản hồi")
            logger.info("🔄 Thử MOVE RELATIVE thay thế...")
            distance = 1000000 if direction > 0 else -1000000
            return self.move_relative(distance, speed)
    
    def move_absolute(self, position: int, speed: int) -> bool:
        """
        Di chuyển tuyệt đối đến vị trí
        
        Args:
            position: Vị trí đích (pulse)
            speed: Tốc độ (pps)
            
        Returns:
            bool: True nếu thành công
        """
        # Kiểm tra giới hạn
        if not (self.config['limits']['min_position'] <= position <= self.config['limits']['max_position']):
            logger.error(f"Vị trí {position} ngoài giới hạn")
            return False
        
        # Chuẩn bị dữ liệu: Position (4 bytes) + Speed (4 bytes)
        data = list(struct.pack('<i', position))  # Signed int
        data.extend(list(struct.pack('<I', speed)))  # Unsigned int
        
        logger.info(f"Move Absolute: Position={position}, Speed={speed}")
        response = self._send_command(FastechCommand.MOVE_ABSOLUTE, data)
        
        if response:
            self._current_status = MotorStatus.MOVING
            return True
        else:
            logger.error("Không thể di chuyển tuyệt đối")
            return False
    
    def move_relative(self, distance: int, speed: int) -> bool:
        """
        Di chuyển tương đối (từ vị trí hiện tại)
        
        Args:
            distance: Khoảng cách di chuyển (pulse, âm = ngược chiều)
            speed: Tốc độ (pps)
            
        Returns:
            bool: True nếu thành công
        """
        # Chuẩn bị dữ liệu: Distance (4 bytes) + Speed (4 bytes)
        data = list(struct.pack('<i', distance))  # Signed int
        data.extend(list(struct.pack('<I', speed)))  # Unsigned int
        
        logger.info(f"Move Relative: Distance={distance}, Speed={speed}")
        response = self._send_command(FastechCommand.MOVE_RELATIVE, data)
        
        if response:
            self._current_status = MotorStatus.MOVING
            return True
        else:
            logger.error("Không thể di chuyển tương đối")
            return False
    
    def homing(self, speed: int = 1000) -> bool:
        """
        Thực hiện Homing (Về gốc)
        
        Args:
            speed: Tốc độ Homing (pps)
            
        Returns:
            bool: True nếu thành công
        """
        # Dữ liệu: Speed (4 bytes)
        data = list(struct.pack('<I', speed))
        
        logger.info(f"Homing với tốc độ {speed} pps")
        response = self._send_command(FastechCommand.HOMING, data)
        
        if response:
            self._current_status = MotorStatus.HOMING
            logger.info("Bắt đầu Homing...")
            return True
        else:
            logger.error("Không thể bắt đầu Homing")
            return False
    
    def read_position(self) -> Optional[int]:
        """
        Đọc vị trí hiện tại của động cơ
        
        Returns:
            int: Vị trí (pulse) hoặc None nếu lỗi
        """
        response = self._send_command(FastechCommand.READ_POSITION)
        
        if response and len(response) >= 11:  # Header(2) + ID(1) + Type(1) + Len(1) + Data(4) + CRC(2)
            # Parse vị trí từ response (4 bytes data, little-endian)
            position_bytes = response[5:9]
            position = struct.unpack('<i', position_bytes)[0]
            self._current_position = position
            return position
        else:
            logger.debug("Không đọc được vị trí")
            return None
    
    def read_status(self) -> Optional[int]:
        """
        Đọc trạng thái động cơ
        
        Returns:
            int: Trạng thái hoặc None nếu lỗi
        """
        response = self._send_command(FastechCommand.READ_STATUS)
        
        if response and len(response) >= 8:
            status_byte = response[5]
            self._current_status = status_byte
            return status_byte
        else:
            return None
    
    def get_current_position(self) -> int:
        """Lấy vị trí hiện tại (từ cache)"""
        return self._current_position
    
    def get_current_status(self) -> int:
        """Lấy trạng thái hiện tại (từ cache)"""
        return self._current_status
    
    def __del__(self):
        """Destructor - Đảm bảo ngắt kết nối"""
        if self.is_connected:
            self.disconnect()
