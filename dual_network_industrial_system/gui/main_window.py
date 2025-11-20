"""
Cửa sổ chính ứng dụng với 2 tabs
"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QMenuBar, QAction, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import logging

from .sht20_tab import SHT20Tab
from .ezistep_tab import EziStepTab

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Cửa sổ chính ứng dụng"""
    
    def __init__(self, sht20_driver, ezistep_driver, data_logger, config):
        super().__init__()
        
        self.sht20_driver = sht20_driver
        self.ezistep_driver = ezistep_driver
        self.data_logger = data_logger
        self.config = config
        
        self.init_ui()
        
        # Timer cho data logging
        if self.config['LOG_CONFIG']['enable']:
            self.log_timer = QTimer()
            self.log_timer.timeout.connect(self.log_system_data)
            self.log_timer.start(self.config['LOG_CONFIG']['log_interval'])
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        # Set window properties
        self.setWindowTitle(self.config['GUI_CONFIG']['window_title'])
        self.setGeometry(100, 100, *self.config['GUI_CONFIG']['window_size'])
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create central widget with tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                color: #212121;
                padding: 12px 30px;
                margin-right: 2px;
                font-size: 12pt;
                font-weight: bold;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #BDBDBD;
            }
        """)
        
        # Create tabs
        self.sht20_tab = SHT20Tab(
            self.sht20_driver,
            self.config['SHT20_CONFIG'],
            self.config['GUI_CONFIG']
        )
        self.ezistep_tab = EziStepTab(
            self.ezistep_driver,
            self.config['EZISTEP_CONFIG'],
            self.config['GUI_CONFIG']
        )
        
        self.tabs.addTab(self.sht20_tab, "🌡️ SHT20 - Giám Sát Môi Trường")
        self.tabs.addTab(self.ezistep_tab, "⚙️ Ezi-STEP - Điều Khiển Động Cơ")
        
        self.setCentralWidget(self.tabs)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Sẵn sàng")
        
        # Apply global stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.config['GUI_CONFIG']['colors']['background']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {self.config['GUI_CONFIG']['colors']['text']};
                font-size: 11pt;
            }}
        """)
    
    def _create_menu_bar(self):
        """Tạo menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        start_log_action = QAction('📝 Bắt đầu Logging', self)
        start_log_action.triggered.connect(self.start_logging)
        file_menu.addAction(start_log_action)
        
        stop_log_action = QAction('⏹️ Dừng Logging', self)
        stop_log_action.triggered.connect(self.stop_logging)
        file_menu.addAction(stop_log_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('🚪 Thoát', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('ℹ️ Giới thiệu', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def start_logging(self):
        """Bắt đầu ghi log"""
        if not self.data_logger.is_logging:
            if self.data_logger.start_logging():
                self.statusBar.showMessage("✅ Đã bắt đầu ghi log", 3000)
                logger.info("User started logging")
            else:
                self.statusBar.showMessage("❌ Không thể bắt đầu ghi log", 3000)
        else:
            self.statusBar.showMessage("⚠️ Đã đang ghi log", 3000)
    
    def stop_logging(self):
        """Dừng ghi log"""
        if self.data_logger.is_logging:
            self.data_logger.stop_logging()
            self.statusBar.showMessage("⏹️ Đã dừng ghi log", 3000)
            logger.info("User stopped logging")
        else:
            self.statusBar.showMessage("⚠️ Không có log đang chạy", 3000)
    
    def log_system_data(self):
        """Ghi dữ liệu hệ thống vào log"""
        if not self.data_logger.is_logging:
            return
        
        # Lấy dữ liệu từ SHT20
        temp, humid = self.sht20_driver.get_last_readings()
        
        # Lấy dữ liệu từ Ezi-STEP
        motor_pos = self.ezistep_driver.get_current_position()
        motor_status = self.ezistep_driver.get_current_status()
        
        # Ghi vào log
        self.data_logger.log_data(
            temperature=temp,
            humidity=humid,
            motor_position=motor_pos,
            motor_status=str(motor_status)
        )
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        about_text = """
        <h2>Hệ Thống Tự Động Hóa Công Nghiệp</h2>
        <h3>Mạng Kép Độc Lập</h3>
        <p><b>Phiên bản:</b> 1.0</p>
        <p><b>Ngày:</b> November 2025</p>
        
        <h4>Tính năng:</h4>
        <ul>
            <li>🌡️ Giám sát môi trường với SHT20 (Modbus RTU @ 9600 bps)</li>
            <li>⚙️ Điều khiển động cơ với Ezi-STEP Plus-R (FASTECH @ 115200 bps)</li>
            <li>📊 Đồ thị realtime</li>
            <li>📝 Ghi log dữ liệu CSV</li>
            <li>🎨 Giao diện đẹp mắt, dễ sử dụng</li>
        </ul>
        
        <h4>Công nghệ:</h4>
        <ul>
            <li>Python 3.8+</li>
            <li>PyQt5 (GUI)</li>
            <li>PyModbus (Modbus RTU)</li>
            <li>PySerial (RS485)</li>
            <li>PyQtGraph (Plotting)</li>
        </ul>
        
        <p><i>Được phát triển cho Hệ thống Tự động hóa Công nghiệp</i></p>
        """
        
        QMessageBox.about(self, "Giới thiệu", about_text)
    
    def closeEvent(self, event):
        """Xử lý khi đóng ứng dụng"""
        reply = QMessageBox.question(
            self,
            'Xác nhận thoát',
            'Bạn có chắc muốn thoát ứng dụng?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Cleanup
            logger.info("Closing application...")
            
            if self.data_logger.is_logging:
                self.data_logger.stop_logging()
            
            self.sht20_tab.cleanup()
            self.ezistep_tab.cleanup()
            
            event.accept()
        else:
            event.ignore()
