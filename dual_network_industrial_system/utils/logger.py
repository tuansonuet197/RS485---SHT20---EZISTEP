"""
Hệ thống Logger cho dự án
Ghi log dữ liệu cảm biến và trạng thái động cơ
"""
import os
import csv
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class DataLogger:
    """Ghi log dữ liệu hệ thống vào file CSV"""
    
    def __init__(self, config: dict):
        """
        Khởi tạo logger
        
        Args:
            config: Dictionary chứa cấu hình (LOG_CONFIG)
        """
        self.config = config
        self.log_file = None
        self.csv_writer = None
        self.is_logging = False
        
        # Tạo thư mục logs nếu chưa có
        if not os.path.exists(config['directory']):
            os.makedirs(config['directory'])
            logger.info(f"Đã tạo thư mục logs: {config['directory']}")
    
    def start_logging(self) -> bool:
        """
        Bắt đầu ghi log
        
        Returns:
            bool: True nếu thành công
        """
        try:
            # Tạo tên file với timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config['filename_prefix']}_{timestamp}.csv"
            filepath = os.path.join(self.config['directory'], filename)
            
            # Mở file CSV
            self.log_file = open(filepath, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.DictWriter(
                self.log_file,
                fieldnames=self.config['csv_fields']
            )
            
            # Ghi header
            self.csv_writer.writeheader()
            self.is_logging = True
            
            logger.info(f"Bắt đầu ghi log vào: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi bắt đầu logging: {e}")
            return False
    
    def stop_logging(self):
        """Dừng ghi log"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None
            self.csv_writer = None
            self.is_logging = False
            logger.info("Đã dừng ghi log")
    
    def log_data(
        self,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        motor_position: Optional[int] = None,
        motor_status: Optional[str] = None
    ):
        """
        Ghi một dòng dữ liệu vào log
        
        Args:
            temperature: Nhiệt độ (°C)
            humidity: Độ ẩm (%RH)
            motor_position: Vị trí động cơ (pulse)
            motor_status: Trạng thái động cơ
        """
        if not self.is_logging or not self.csv_writer:
            return
        
        try:
            # Tạo dòng dữ liệu
            row = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'temperature': f"{temperature:.2f}" if temperature is not None else "N/A",
                'humidity': f"{humidity:.2f}" if humidity is not None else "N/A",
                'motor_position': str(motor_position) if motor_position is not None else "N/A",
                'motor_status': motor_status if motor_status else "N/A"
            }
            
            # Ghi vào file
            self.csv_writer.writerow(row)
            self.log_file.flush()  # Đảm bảo dữ liệu được ghi ngay
            
        except Exception as e:
            logger.error(f"Lỗi khi ghi log: {e}")
    
    def __del__(self):
        """Destructor - Đảm bảo đóng file"""
        if self.is_logging:
            self.stop_logging()


def setup_console_logging(level=logging.INFO):
    """
    Cấu hình logging cho console
    
    Args:
        level: Mức độ logging (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
