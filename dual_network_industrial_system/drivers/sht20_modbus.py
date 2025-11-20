"""
Driver cho Cảm biến SHT20 - Giao thức Modbus RTU
Hỗ trợ đọc nhiệt độ và độ ẩm qua RS485
"""
import logging
from typing import Optional, Tuple
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import time

logger = logging.getLogger(__name__)


class SHT20ModbusDriver:
    """Driver điều khiển cảm biến SHT20 qua Modbus RTU"""
    
    def __init__(self, config: dict):
        """
        Khởi tạo driver SHT20
        
        Args:
            config: Dictionary chứa cấu hình (SHT20_CONFIG)
        """
        self.config = config
        self.client: Optional[ModbusSerialClient] = None
        self.is_connected = False
        self._last_temperature = None
        self._last_humidity = None
        
        logger.info("SHT20 Driver initialized")
    
    def connect(self) -> bool:
        """
        Kết nối tới cảm biến SHT20
        
        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            self.client = ModbusSerialClient(
                port=self.config['port'],
                baudrate=self.config['baudrate'],
                bytesize=self.config['data_bits'],
                stopbits=self.config['stop_bits'],
                parity=self.config['parity'],
                timeout=self.config['timeout']
            )
            
            if self.client.connect():
                self.is_connected = True
                logger.info(f"Đã kết nối SHT20 trên {self.config['port']} @ {self.config['baudrate']} bps")
                
                # Test đọc để kiểm tra kết nối (không bắt buộc phải thành công)
                try:
                    temp, hum = self.read_sensor_data()
                    if temp is not None:
                        logger.info(f"Test đọc thành công: {temp}°C, {hum}%RH")
                    else:
                        logger.warning("Kết nối được nhưng không đọc được dữ liệu. Kiểm tra dây nối và địa chỉ Slave ID.")
                except Exception as e:
                    logger.warning(f"Test đọc gặp lỗi: {e}. Kết nối vẫn được thiết lập.")
                
                return True
            else:
                logger.error(f"Không thể kết nối tới {self.config['port']}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi kết nối SHT20: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Ngắt kết nối khỏi cảm biến"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Đã ngắt kết nối SHT20")
    
    def read_temperature(self) -> Optional[float]:
        """
        Đọc nhiệt độ từ cảm biến
        
        Returns:
            float: Nhiệt độ (°C) hoặc None nếu lỗi
        """
        if not self.is_connected or not self.client:
            logger.warning("Chưa kết nối tới SHT20")
            return None
        
        try:
            # Đọc thanh ghi nhiệt độ (Function Code 0x03 hoặc 0x04)
            result = self.client.read_input_registers(
                address=self.config['registers']['temperature'],
                count=1,
                device_id=self.config['slave_id']
            )
            
            if result.isError():
                logger.error(f"Lỗi đọc nhiệt độ: {result}")
                return None
            
            # Quy đổi: Giá trị / 10 (VD: 255 -> 25.5°C)
            raw_value = result.registers[0]
            temperature = raw_value / 10.0
            
            # Kiểm tra giới hạn
            if not (self.config['limits']['temp_min'] <= temperature <= self.config['limits']['temp_max']):
                logger.warning(f"Nhiệt độ ngoài giới hạn: {temperature}°C")
            
            self._last_temperature = temperature
            return temperature
            
        except ModbusException as e:
            logger.error(f"Modbus exception khi đọc nhiệt độ: {e}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi đọc nhiệt độ: {e}")
            return None
    
    def read_humidity(self) -> Optional[float]:
        """
        Đọc độ ẩm từ cảm biến
        
        Returns:
            float: Độ ẩm (%RH) hoặc None nếu lỗi
        """
        if not self.is_connected or not self.client:
            logger.warning("Chưa kết nối tới SHT20")
            return None
        
        try:
            # Đọc thanh ghi độ ẩm
            result = self.client.read_input_registers(
                address=self.config['registers']['humidity'],
                count=1,
                device_id=self.config['slave_id']
            )
            
            if result.isError():
                logger.error(f"Lỗi đọc độ ẩm: {result}")
                return None
            
            # Quy đổi: Giá trị / 10 (VD: 605 -> 60.5%RH)
            raw_value = result.registers[0]
            humidity = raw_value / 10.0
            
            # Kiểm tra giới hạn
            if not (self.config['limits']['humidity_min'] <= humidity <= self.config['limits']['humidity_max']):
                logger.warning(f"Độ ẩm ngoài giới hạn: {humidity}%RH")
            
            self._last_humidity = humidity
            return humidity
            
        except ModbusException as e:
            logger.error(f"Modbus exception khi đọc độ ẩm: {e}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi đọc độ ẩm: {e}")
            return None
    
    def read_sensor_data(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Đọc cả nhiệt độ và độ ẩm cùng lúc
        
        Returns:
            tuple: (nhiệt độ, độ ẩm) hoặc (None, None) nếu lỗi
        """
        temperature = self.read_temperature()
        time.sleep(0.05)  # Delay nhỏ giữa các lệnh đọc
        humidity = self.read_humidity()
        
        return temperature, humidity
    
    def get_last_readings(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Lấy giá trị đọc gần nhất (không giao tiếp với thiết bị)
        
        Returns:
            tuple: (nhiệt độ, độ ẩm) đã lưu
        """
        return self._last_temperature, self._last_humidity
    
    def read_device_id(self) -> Optional[int]:
        """
        Đọc Slave ID của thiết bị
        
        Returns:
            int: Slave ID hoặc None nếu lỗi
        """
        if not self.is_connected or not self.client:
            return None
        
        try:
            result = self.client.read_holding_registers(
                address=self.config['registers']['device_id'],
                count=1,
                device_id=self.config['slave_id']
            )
            
            if not result.isError():
                return result.registers[0]
            return None
            
        except Exception as e:
            logger.error(f"Lỗi đọc device ID: {e}")
            return None
    
    def change_device_id(self, new_id: int) -> bool:
        """
        Thay đổi Slave ID của thiết bị (1-247)
        
        Args:
            new_id: ID mới (1-247)
            
        Returns:
            bool: True nếu thành công
        """
        if not (1 <= new_id <= 247):
            logger.error("ID phải trong khoảng 1-247")
            return False
        
        if not self.is_connected or not self.client:
            logger.warning("Chưa kết nối tới SHT20")
            return False
        
        try:
            result = self.client.write_register(
                address=self.config['registers']['device_id'],
                value=new_id,
                device_id=self.config['slave_id']
            )
            
            if not result.isError():
                logger.info(f"Đã đổi Slave ID thành {new_id}")
                self.config['slave_id'] = new_id
                return True
            else:
                logger.error("Không thể thay đổi Slave ID")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi thay đổi Slave ID: {e}")
            return False
    
    def __del__(self):
        """Destructor - Đảm bảo ngắt kết nối"""
        if self.is_connected:
            self.disconnect()
