import log
import checkNet
import utime
import _thread
from queue import Queue
import usocket
from machine import UART

# === Config ===
PROJECT_NAME = "QuecPython_RS485_SoilSensor_TCP"
PROJECT_VERSION = "1.0.0"
IMEI = "862942071230965"  # 15-digit IMEI

TCP_SERVER_IP = "13.126.118.139"
TCP_SERVER_PORT = 9619

# === Setup Logging and Network ===
checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
log.basicConfig(level=log.INFO)

# === Utility: Timestamp in YYMMddhhmmss format ===
# === Utility: Timestamp in BCD format (YY MM dd hh mm ss) ===
def get_timestamp_bytes():
    t = utime.localtime()  # (year, month, day, hour, minute, second, wday, yday)
    def to_bcd(n):
        return ((n // 10) << 4) | (n % 10)

    return bytearray([
        to_bcd(t[0] % 100),  # YY (last 2 digits of year)
        to_bcd(t[1]),        # MM
        to_bcd(t[2]),        # DD
        to_bcd(t[3]),        # hh
        to_bcd(t[4]),        # mm
        to_bcd(t[5])         # ss
    ])

# === Sensor UART Handler ===
class SoilSensorUART:
    def __init__(self, uart_no=UART.UART2, baud=9600, data_bits=8, parity=0, stop_bits=1, flow_control=0):
        self.uart = UART(uart_no, baud, data_bits, parity, stop_bits, flow_control)
        self._queue = Queue(5)
        self.decoded_values = None
        _thread.start_new_thread(self.handler_thread, ())
        self.uart.set_callback(self.callback)
        self.query_command = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x08, 0x44, 0x0C])

    def callback(self, event):
        if event[0] == 0:
            self._queue.put(event[2])

    def send_query(self):
        self.uart.write(self.query_command)
        print("Query sent:", [hex(x) for x in self.query_command])

    def handler_thread(self):
        while True:
            recv_len = self._queue.get()
            response = self.uart.read(recv_len)
            if response and response[0:3] == bytearray([0x01, 0x03, 0x10]):
                temp = (response[3] << 8) | response[4]
                hum  = (response[5] << 8) | response[6]
                ec   = (response[7] << 8) | response[8]
                ph   = (response[9] << 8) | response[10]
                n    = (response[11] << 8) | response[12]
                p    = (response[13] << 8) | response[14]
                k    = (response[15] << 8) | response[16]
                sal  = (response[17] << 8) | response[18]

                self.decoded_values = {
                    'temperature': temp,
                    'humidity': hum,
                    'ec': ec,
                    'ph': ph,
                    'nitrogen': n,
                    'phosphor': p,
                    'potassium': k,
                    'salinity': sal
                }

                print("Decoded Sensor Values:")
                print("  Temperature: %.1f °C" % (temp / 10.0))
                print("  Humidity:    %.1f %%" % (hum / 10.0))
                print("  EC:          %d µS/cm" % ec)
                print("  pH:          %.2f" % (ph / 100.0))
                print("  Nitrogen:    %d mg/kg" % n)
                print("  Phosphor:    %d mg/kg" % p)
                print("  Potassium:   %d mg/kg" % k)
                print("  Salinity:    %d mg/L" % sal)
            else:
                print("Unexpected or invalid Modbus response.")
                self.decoded_values = None

    def get_scaled_data_packet(self):
        if not self.decoded_values:
            return None

        timestamp = get_timestamp_bytes()

        sensor_payload = bytearray()
        for key in ['temperature', 'humidity', 'ec', 'ph', 'nitrogen', 'phosphor', 'potassium', 'salinity']:
            val = self.decoded_values[key]
            sensor_payload.append((val >> 8) & 0xFF)
            sensor_payload.append(val & 0xFF)

        packet = bytearray()
        packet.append(0x78)               # START BYTE
        packet.append(0x02)               # PROTOCOL INDEX for sensor data
        packet.extend(timestamp)          # 6-byte timestamp
        packet.extend(sensor_payload)     # 16-byte sensor data
        packet.append(0x79)               # END BYTE
        return packet

# === Build Login Packet with BCD IMEI and Wrapping ===
def build_login_packet(imei):
    if len(imei) != 15 or not imei.isdigit():
        raise ValueError("IMEI must be a 15-digit number")
    padded = "0" + imei  # Make 16 digits for BCD
    bcd = bytearray()
    for i in range(0, 16, 2):
        bcd.append((int(padded[i]) << 4) | int(padded[i + 1]))

    packet = bytearray()
    packet.append(0x78)        # START BYTE
    packet.append(0x01)        # PROTOCOL INDEX for login
    packet.extend(bcd)         # IMEI in BCD
    packet.append(0x79)        # END BYTE
    return packet

# === TCP Communication Handler ===
def persistent_tcp_send(login_bytes, server_ip, server_port, sensor):
    s = None
    connected = False

    while True:
        try:
            if not connected:
                print("Connecting to TCP server...")
                s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((server_ip, server_port))
                print("Connected.")

                # Send login packet
                print("Sending login packet:", [hex(b) for b in login_bytes])
                s.send(login_bytes)

                # Wait for response before sending sensor data
                resp = s.recv(64)
                print("Server response:", resp)
                connected = True

            # Query sensor and get decoded data
            sensor.decoded_values = None
            sensor.send_query()

            retries = 5
            while not sensor.decoded_values and retries > 0:
                utime.sleep(1)
                retries -= 1

            packet = sensor.get_scaled_data_packet()
            if packet:
                s.send(packet)
                print("Sensor data packet sent:", [hex(b) for b in packet])
            else:
                print("No valid sensor data this cycle.")

            utime.sleep(30)

        except Exception as e:
            print("Connection error:", e)
            if s:
                try:
                    s.close()
                except:
                    pass
            s = None
            connected = False
            print("Reconnecting in 5 seconds...")
            utime.sleep(5)

# === Main Entry Point ===
if __name__ == '__main__':
    print("Waiting for network...")
    stagecode, subcode = checknet.wait_network_connected(30)

    if stagecode == 3 and subcode == 1:
        print("Network connected.")
        try:
            sensor = SoilSensorUART()
            utime.sleep(1)  # Allow UART to stabilize
            login_packet = build_login_packet(IMEI)
            persistent_tcp_send(login_packet, TCP_SERVER_IP, TCP_SERVER_PORT, sensor)
        except Exception as e:
            print("Fatal error:", str(e))
    else:
        print("Network failed: stagecode={}, subcode={}".format(stagecode, subcode))
