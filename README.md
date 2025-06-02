# Soil_Wheelseye_Quecpython

QuecPython RS485 Soil Sensor TCP
Overview
This project, QuecPython_RS485_SoilSensor_TCP, is a MicroPython-based application designed for QuecPython-enabled devices to interface with an RS485 soil sensor and transmit data over TCP to a remote server. It reads soil parameters such as temperature, humidity, EC, pH, nitrogen, phosphorus, potassium, and salinity, and sends them in a structured packet format along with a timestamp and device IMEI.
Features

RS485 Soil Sensor Interface: Communicates with a soil sensor via UART using the Modbus protocol.
TCP Communication: Establishes a persistent TCP connection to a remote server to send sensor data and login packets.
Timestamp Generation: Includes a BCD-encoded timestamp in YYMMddhhmmss format.
Error Handling: Implements robust reconnection logic for TCP communication and retries for sensor data collection.
Logging: Uses the log module for debugging and monitoring.

Requirements

Hardware:
QuecPython-enabled microcontroller (e.g., Quectel module).
RS485 soil sensor connected via UART (default: UART2, 9600 baud).


Software:
MicroPython with QuecPython extensions.
Required libraries: log, checkNet, utime, _thread, queue, usocket, machine.



Configuration
Edit the following constants in the code to match your setup:

PROJECT_NAME: Name of the project ("QuecPython_RS485_SoilSensor_TCP").
PROJECT_VERSION: Version of the project ("1.0.0").
IMEI: 15-digit device IMEI (e.g., "862942071230965").
TCP_SERVER_IP: IP address of the TCP server (e.g., "13.126.118.139").
TCP_SERVER_PORT: Port of the TCP server (e.g., 9619).

Code Structure

Utility Functions:
get_timestamp_bytes(): Generates a 6-byte BCD timestamp (YYMMddhhmmss).
build_login_packet(imei): Creates a login packet with the device's IMEI in BCD format.


SoilSensorUART Class:
Initializes UART communication with the soil sensor.
Sends Modbus query commands and processes responses.
Decodes sensor data (temperature, humidity, EC, pH, nitrogen, phosphorus, potassium, salinity).
Formats data into a 16-byte payload with start/end bytes and protocol index.


TCP Communication:
persistent_tcp_send(): Manages TCP connection, sends login packet, and periodically transmits sensor data.


Main Loop:
Waits for network connectivity using checkNet.
Initializes the sensor and starts the TCP communication loop.



Packet Formats

Login Packet:
Start Byte: 0x78
Protocol Index: 0x01 (login)
IMEI: 8 bytes (BCD-encoded, padded with leading zero)
End Byte: 0x79


Sensor Data Packet:
Start Byte: 0x78
Protocol Index: 0x02 (sensor data)
Timestamp: 6 bytes (BCD YYMMddhhmmss)
Sensor Data: 16 bytes (2 bytes per parameter: temperature, humidity, EC, pH, nitrogen, phosphorus, potassium, salinity)
End Byte: 0x79



Usage

Ensure the RS485 soil sensor is connected to the correct UART pins (default: UART2).
Update the configuration constants (IMEI, TCP_SERVER_IP, TCP_SERVER_PORT) as needed.
Upload the code to a QuecPython-compatible device.
The device will:
Wait for network connectivity.
Initialize the soil sensor.
Establish a TCP connection and send a login packet.
Periodically query the sensor and send data every 30 seconds.


Monitor the console output for debugging information (sensor values, connection status).

Error Handling

Network Issues: The code waits for network connectivity and retries if the network is unavailable.
TCP Connection: Reconnects every 5 seconds on failure.
Sensor Data: Retries up to 5 times if no valid data is received, skipping the cycle if unsuccessful.

Debugging

The log module outputs to the console at the INFO level.
Sensor data and TCP communication status are printed for monitoring.
Invalid Modbus responses are logged for troubleshooting.

Notes

The soil sensor must respond to the Modbus query 0x01 0x03 0x00 0x00 0x00 0x08 0x44 0x0C.
Ensure the TCP server is configured to accept the login and sensor data packets in the specified format.
The code assumes a stable power supply and proper RS485 wiring.

License
This project is provided as-is for educational and development purposes. No warranty is implied.
