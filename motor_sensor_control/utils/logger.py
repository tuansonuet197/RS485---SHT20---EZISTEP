"""Data logging utilities"""

import os
import csv
from datetime import datetime
import config

class DataLogger:
    """Logger for sensor data and system events"""
    
    def __init__(self):
        self.log_dir = config.LOG_DIR
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        self.csv_file = None
        self.csv_writer = None
        
        if config.LOG_CSV_ENABLED:
            self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"data_log_{timestamp}.csv")
        
        self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'Timestamp', 'Temperature_C', 'Humidity_RH', 
            'Motor_Position', 'Motor_Status'
        ])
        print(f"CSV logging started: {filename}")
    
    def log_sensor_data(self, temp: float, humidity: float, 
                       motor_pos: int, motor_status: str):
        """Log sensor and motor data to CSV"""
        if self.csv_writer:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.csv_writer.writerow([
                timestamp, f"{temp:.2f}", f"{humidity:.2f}",
                motor_pos, motor_status
            ])
            self.csv_file.flush()
    
    def info(self, message: str):
        """Log info message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] INFO: {message}")
    
    def warning(self, message: str):
        """Log warning message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] WARNING: {message}")
    
    def error(self, message: str):
        """Log error message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}")
    
    def close(self):
        """Close log files"""
        if self.csv_file:
            self.csv_file.close()
