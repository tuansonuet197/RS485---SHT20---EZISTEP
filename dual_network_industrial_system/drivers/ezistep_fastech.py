"""
Driver Động cơ Bước Ezi-STEP Plus-R - FASTECH Protocol
Bài tập lớn: Kiến trúc máy tính và mạng truyền thông công nghiệp

Triển khai:
- Giao thức FASTECH qua RS-485 @ 115200 bps
- Byte stuffing/destuffing (duplicate 0xAA)
- CRC-16 (Modbus RTU standard)
- Điều khiển chuyển động: JOG, Absolute, Relative, Homing

Tham khảo: FASTECH Ezi-STEP Plus-R Communication Manual
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
    MOVE_VELOCITY = 0x37  # JOG/Move with velocity
    MOVE_ABSOLUTE = 0x38
    MOVE_RELATIVE = 0x39
    STOP = 0x31
    SERVO_ON = 0x83
    SERVO_OFF = 0x84
    ALARM_RESET = 0x04
    READ_POSITION = 0x0C
    READ_STATUS = 0x0D


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
        
        # Protocol constants
        self.HEADER = bytes([0xAA, 0x55])
        self.TAIL = bytes([0xAA, 0x0D])
        self.SLAVE_ID = config['slave_id']
        
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
    
    def _calculate_crc(self, data: bytes) -> int:
        """
        Tính CRC-16 cho gói tin FASTECH (Modbus RTU CRC)
        
        Args:
            data: Byte cần tính CRC
            
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
    
    def _byte_stuffing(self, frame_data: bytes) -> bytearray:
        """
        Byte stuffing: Thêm 0xAA sau mỗi 0xAA trong data
        
        Args:
            frame_data: Dữ liệu cần stuffing
            
        Returns:
            bytearray: Dữ liệu đã được stuffing
        """
        stuffed_data = bytearray()
        for byte in frame_data:
            stuffed_data.append(byte)
            if byte == 0xAA:
                stuffed_data.append(0xAA)  # Duplicate 0xAA
        return stuffed_data
    
    def _byte_destuffing(self, stuffed_data: bytes) -> bytearray:
        """
        Byte destuffing: Loại bỏ 0xAA thừa
        
        Args:
            stuffed_data: Dữ liệu đã stuffing
            
        Returns:
            bytearray: Dữ liệu gốc
        """
        destuffed_data = bytearray()
        i = 0
        while i < len(stuffed_data):
            destuffed_data.append(stuffed_data[i])
            if stuffed_data[i] == 0xAA and i + 1 < len(stuffed_data) and stuffed_data[i + 1] == 0xAA:
                i += 1  # Skip duplicate 0xAA
            i += 1
        return destuffed_data
    
    def _build_packet(self, frame_type: int, data: bytes = b'') -> bytes:
        """
        Xây dựng gói tin FASTECH Protocol với byte stuffing
        
        Format: HEADER + [SlaveID + FrameType + Data + CRC] + TAIL
                          └─────── Byte Stuffing ────────┘
        
        Args:
            frame_type: Mã lệnh (Command code)
            data: Dữ liệu lệnh (bytes)
            
        Returns:
            bytes: Gói tin hoàn chỉnh
        """
        # 1. Frame core = SlaveID + FrameType + Data
        frame_core = struct.pack('<B', self.SLAVE_ID) + struct.pack('<B', frame_type) + data
        
        # 2. Tính CRC cho frame_core
        crc_val = self._calculate_crc(frame_core)
        crc_bytes = struct.pack('<H', crc_val)
        
        # 3. Byte stuffing cho (frame_core + CRC)
        data_to_stuff = frame_core + crc_bytes
        stuffed_frame_data = self._byte_stuffing(data_to_stuff)
        
        # 4. Header + Stuffed Data + Tail
        packet = self.HEADER + stuffed_frame_data + self.TAIL
        
        return bytes(packet)
    
    def _decode_status_byte(self, status_byte: int) -> str:
        """Decode status byte từ phản hồi Ezi-STEP"""
        status_bits = []
        if status_byte & 0x80:
            status_bits.append("📍ACK")
        if status_byte & 0x02:
            status_bits.append("❌ALARM")
        
        return f"0x{status_byte:02X}[{' '.join(status_bits) if status_bits else 'OK'}]"
    
    def _send_command(self, frame_type: int, data: bytes = b'') -> Optional[bytes]:
        """
        Gửi lệnh và nhận phản hồi với byte destuffing
        
        Args:
            frame_type: Mã lệnh
            data: Dữ liệu lệnh (bytes)
            
        Returns:
            bytes: Phản hồi từ driver (đã destuffing) hoặc None nếu lỗi
        """
        if not self.is_connected or not self.serial_port:
            logger.warning("Chưa kết nối tới Ezi-STEP")
            return None
        
        try:
            # Xây dựng và gửi gói tin
            packet = self._build_packet(frame_type, data)
            logger.debug(f"📤 Gửi (0x{frame_type:02X}): {packet.hex().upper()}")
            self.serial_port.write(packet)
            
            # Đợi phản hồi
            time.sleep(0.05)
            
            # Đọc phản hồi
            if self.serial_port.in_waiting > 0:
                response_raw = self.serial_port.read(self.serial_port.in_waiting)
                logger.debug(f"📥 Nhận: {response_raw.hex().upper()}")
                
                # Parse response: HEADER + stuffed_data + TAIL
                if len(response_raw) < 6:
                    logger.warning("Phản hồi quá ngắn")
                    return None
                
                # Remove header and tail
                if response_raw[:2] == self.HEADER and response_raw[-2:] == self.TAIL:
                    stuffed_data = response_raw[2:-2]
                    # Destuffing
                    destuffed_data = self._byte_destuffing(stuffed_data)
                    
                    # Parse: SlaveID + FrameType + Data + CRC
                    if len(destuffed_data) >= 4:
                        slave_id = destuffed_data[0]
                        resp_frame_type = destuffed_data[1]
                        data_and_crc = destuffed_data[2:]
                        
                        # Verify CRC
                        if len(data_and_crc) >= 2:
                            received_crc = struct.unpack('<H', data_and_crc[-2:])[0]
                            calc_crc = self._calculate_crc(destuffed_data[:-2])
                            
                            if received_crc == calc_crc:
                                logger.info(f"✅ CRC OK, Frame: 0x{resp_frame_type:02X}")
                                return destuffed_data
                            else:
                                logger.warning(f"❌ CRC mismatch: {received_crc:04X} != {calc_crc:04X}")
                    
                return response_raw
            else:
                logger.warning(f"Không nhận được phản hồi cho lệnh 0x{frame_type:02X}")
                return None
                
        except serial.SerialException as e:
            logger.error(f"Lỗi Serial: {e}")
            return None
        except Exception as e:
            logger.error(f"Lỗi: {e}")
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
        Bật Servo (Enable động cơ)
        
        Returns:
            bool: True nếu thành công
        """
        logger.info("🔌 SERVO ON...")
        
        # Reset alarm trước
        self.alarm_reset()
        time.sleep(0.1)
        
        response = self._send_command(FastechCommand.SERVO_ON)
        if response:
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
        Di chuyển Jog (MoveVelocity) - FIXED theo Ezi2.py/Ezi3.py
        
        Format: Command 0x37 + Data[Velocity(4 bytes LE) + Direction(1 byte)]
        
        Args:
            speed: Tốc độ (pps)
            direction: 1 = CW, 0 = CCW
            
        Returns:
            bool: True nếu thành công
        """
        if speed < 1000:
            logger.warning(f"⚠️ Tốc độ {speed} pps quá thấp! Tăng lên 5000 pps")
            speed = 5000
        
        dir_str = "CW ➡️" if direction > 0 else "CCW ⬅️"
        logger.info(f"🏃 JOG {dir_str} @ {speed} pps")
        
        # Data format theo Ezi2.py/Ezi3.py: Velocity(4 bytes LE) + Direction(1 byte)
        command_data = struct.pack('<LB', abs(speed), 1 if direction > 0 else 0)
        
        logger.debug(f"📦 Data: {command_data.hex().upper()}")
        
        response = self._send_command(FastechCommand.MOVE_VELOCITY, command_data)
        
        if response:
            self._current_status = MotorStatus.MOVING
            logger.info("✅ JOG command sent successfully")
            return True
        else:
            logger.error("❌ JOG failed")
            return False
    
    def move_absolute(self, position: int, speed: int) -> bool:
        """
        Di chuyển tuyệt đối đến vị trí
        
        Args:
            position: Vị trí đích (pulse)
            speed: Tốc độ (pps)
            
        Returns:
            bool: True nếu thành công
        """
        if not (self.config['limits']['min_position'] <= position <= self.config['limits']['max_position']):
            logger.error(f"Vị trí {position} ngoài giới hạn")
            return False
        
        # Data: Position(4 bytes LE) + Speed(4 bytes LE)
        command_data = struct.pack('<iI', position, speed)
        
        logger.info(f"Move Absolute: Position={position}, Speed={speed}")
        response = self._send_command(FastechCommand.MOVE_ABSOLUTE, command_data)
        
        if response:
            self._current_status = MotorStatus.MOVING
            return True
        else:
            logger.error("Move absolute failed")
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
        # Data: Distance(4 bytes LE) + Speed(4 bytes LE)
        command_data = struct.pack('<iI', distance, speed)
        
        logger.info(f"Move Relative: Distance={distance}, Speed={speed}")
        response = self._send_command(FastechCommand.MOVE_RELATIVE, command_data)
        
        if response:
            self._current_status = MotorStatus.MOVING
            return True
        else:
            logger.error("Move relative failed")
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
        
        if response and len(response) >= 6:
            # Destuffed data: [SlaveID, FrameType, Data..., CRC_L, CRC_H]
            # Position = 4 bytes starting at index 2
            if len(response) >= 8:
                position = struct.unpack('<i', response[2:6])[0]
                self._current_position = position
                logger.debug(f"Position: {position}")
                return position
        logger.debug("Không đọc được vị trí")
        return None
    
    def read_status(self) -> Optional[int]:
        """
        Đọc trạng thái động cơ
        
        Returns:
            int: Trạng thái hoặc None nếu lỗi
        """
        response = self._send_command(FastechCommand.READ_STATUS)
        
        if response and len(response) >= 4:
            # Destuffed data: [SlaveID, FrameType, Status_Data..., CRC_L, CRC_H]
            status_byte = response[2] if len(response) > 2 else 0
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
