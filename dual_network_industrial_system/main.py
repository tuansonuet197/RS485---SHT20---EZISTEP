"""
Ứng dụng chính - Hệ Thống Tự Động Hóa Công Nghiệp
Dual Network Industrial System

Chạy ứng dụng:
    python main.py
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication

# Import configurations
from config import (
    SHT20_CONFIG,
    EZISTEP_CONFIG,
    GUI_CONFIG,
    LOG_CONFIG,
    SYSTEM_CONFIG
)

# Import drivers
from drivers import SHT20ModbusDriver, EziStepFastechDriver

# Import utilities
from utils import DataLogger, setup_console_logging

# Import GUI
from gui import MainWindow


def main():
    """Entry point của ứng dụng"""
    # Setup logging (DEBUG để xem chi tiết giao tiếp)
    setup_console_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("HỆ THỐNG TỰ ĐỘNG HÓA CÔNG NGHIỆP - MẠNG KÉP")
    logger.info("=" * 60)
    logger.info("Khởi động ứng dụng...")
    
    try:
        # Khởi tạo drivers
        logger.info("Khởi tạo SHT20 Driver (Modbus RTU @ 9600 bps)...")
        sht20_driver = SHT20ModbusDriver(SHT20_CONFIG)
        
        logger.info("Khởi tạo Ezi-STEP Driver (FASTECH @ 115200 bps)...")
        ezistep_driver = EziStepFastechDriver(EZISTEP_CONFIG)
        
        # Khởi tạo data logger
        logger.info("Khởi tạo Data Logger...")
        data_logger = DataLogger(LOG_CONFIG)
        
        # Tạo QApplication
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Modern style
        
        # Tạo và hiển thị main window
        logger.info("Khởi tạo GUI...")
        config_dict = {
            'SHT20_CONFIG': SHT20_CONFIG,
            'EZISTEP_CONFIG': EZISTEP_CONFIG,
            'GUI_CONFIG': GUI_CONFIG,
            'LOG_CONFIG': LOG_CONFIG,
            'SYSTEM_CONFIG': SYSTEM_CONFIG
        }
        
        main_window = MainWindow(
            sht20_driver=sht20_driver,
            ezistep_driver=ezistep_driver,
            data_logger=data_logger,
            config=config_dict
        )
        
        main_window.show()
        logger.info("✅ Ứng dụng đã sẵn sàng!")
        logger.info("")
        logger.info("Hướng dẫn sử dụng:")
        logger.info("1. Tab SHT20: Nhấn 'Kết nối' để kết nối cảm biến")
        logger.info("2. Tab Ezi-STEP: Nhấn 'Kết nối' -> 'Servo ON' để bật động cơ")
        logger.info("3. Menu File: Bật/Tắt logging dữ liệu")
        logger.info("")
        
        # Run application
        exit_code = app.exec_()
        
        logger.info("Ứng dụng đã đóng")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
