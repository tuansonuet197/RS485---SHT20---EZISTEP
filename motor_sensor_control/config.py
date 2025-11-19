"""Configuration file for Motor & Sensor Control System"""

# RS485 Communication Settings
RS485_TIMEOUT = 0.5  # seconds

# SHT20 Sensor Settings
SHT20_PORT = "COM1"  # COM port cho SHT20
SHT20_SLAVE_ID = 1
SHT20_BAUDRATE = 9600  # SHT20 RS485 default baudrate
TEMP_POLL_INTERVAL = 2000  # milliseconds

# EziSTEP Motor Settings
EZISTEP_PORT = "COM2"  # COM port cho EziSTEP
EZISTEP_SLAVE_ID = 2
EZISTEP_BAUDRATE = 115200  # EziSTEP default baudrate
DEFAULT_MOTOR_SPEED = 50000  # pps (pulses per second)
DEFAULT_JOG_SPEED = 10000  # pps

# Automation Settings
AUTO_MODE_ENABLED = False
AUTO_TEMP_HIGH = 30.0  # Celsius
AUTO_TEMP_LOW = 20.0
AUTO_HUMIDITY_HIGH = 70.0  # %RH
AUTO_HUMIDITY_LOW = 40.0

# Motor positions for automation
MOTOR_POS_TEMP_HIGH = 10000  # pulse
MOTOR_POS_TEMP_LOW = -10000
MOTOR_POS_HUMIDITY_HIGH = 5000
MOTOR_POS_HUMIDITY_LOW = -5000

# Logging
LOG_DIR = "logs"
LOG_CSV_ENABLED = True
