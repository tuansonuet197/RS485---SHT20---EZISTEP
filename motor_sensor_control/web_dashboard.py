"""
Web Dashboard Server for SHT20 Sensor
Simple HTTP server with real-time sensor data
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from devices.rs485_manager import RS485Manager
from devices.sht20_modbus import SHT20Modbus
import config

# Global sensor instance
rs485 = None
sht20 = None
last_data = {'temperature': None, 'humidity': None}

def init_sensor():
    """Initialize SHT20 sensor"""
    global rs485, sht20
    try:
        rs485 = RS485Manager(config.SHT20_PORT, config.SHT20_BAUDRATE)
        if rs485.connect():
            sht20 = SHT20Modbus(rs485, config.SHT20_SLAVE_ID)
            print(f"✅ SHT20 connected on {config.SHT20_PORT}")
            return True
        else:
            print(f"❌ Failed to connect to {config.SHT20_PORT}")
            return False
    except Exception as e:
        print(f"❌ Error initializing sensor: {e}")
        return False

def read_sensor_data():
    """Read current sensor data"""
    global last_data
    if sht20:
        try:
            data = sht20.read_temp_humidity()
            if data:
                last_data['temperature'] = data[0]
                last_data['humidity'] = data[1]
                return last_data
        except Exception as e:
            print(f"Error reading sensor: {e}")
    return last_data

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to reduce console spam"""
        pass
    
    def do_GET(self):
        if self.path == '/':
            # Serve HTML dashboard
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read HTML file
            html_file = os.path.join(os.path.dirname(__file__), 'dashboard.html')
            with open(html_file, 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/data':
            # Serve JSON data
            data = read_sensor_data()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(data).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

def main():
    """Run web server"""
    print("=" * 60)
    print("  SHT20 SENSOR WEB DASHBOARD")
    print("=" * 60)
    print()
    
    # Initialize sensor
    if not init_sensor():
        print("\n⚠️  Warning: Sensor not connected")
        print("   Dashboard will run but show no data")
        print()
    
    # Start web server
    port = 8080
    server = HTTPServer(('localhost', port), DashboardHandler)
    
    print(f"🌐 Dashboard running at: http://localhost:{port}")
    print(f"📊 Sensor: SHT20 on {config.SHT20_PORT}")
    print(f"🔄 Update interval: 2 seconds")
    print()
    print("Press Ctrl+C to stop server")
    print("=" * 60)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        if rs485:
            rs485.disconnect()

if __name__ == '__main__':
    main()
