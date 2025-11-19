"""Main application entry point - Simple version"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt
import config

class SimpleMainWindow(QMainWindow):
    """Simple main window for testing"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motor & Sensor Control System")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Title
        title = QLabel("He Thong Dieu Khien Motor va Cam Bien")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info label
        info = QLabel(f"SHT20: {config.SHT20_PORT} | EziSTEP: {config.EZISTEP_PORT}")
        info.setStyleSheet("padding: 5px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Log text edit
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        # Test button
        btn = QPushButton("Test Connection")
        btn.setStyleSheet("padding: 10px; font-size: 14px;")
        btn.clicked.connect(self.test_connection)
        layout.addWidget(btn)
        
        # Initial log
        self.log.append("=== System Started ===")
        self.log.append("Ready to connect...")
        self.log.append("")
        self.log.append("Note: This is a basic version.")
        self.log.append("Full GUI will be generated from mainwindow.ui")
    
    def test_connection(self):
        """Test button clicked"""
        self.log.append("\n[INFO] Testing connection...")
        self.log.append("Please connect hardware and run proper tests")
        self.log.append("Use: python test_devices.py sht20")
        self.log.append("Use: python test_devices.py motor")

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SimpleMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
