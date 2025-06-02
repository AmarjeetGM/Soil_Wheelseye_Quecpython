# Soil_Wheelseye_Quecpython

QuecPython RS485 Soil Sensor TCP
Project Overview

Name: QuecPython_RS485_SoilSensor_TCP
Version: 1.0.0
Description: A MicroPython application for QuecPython-enabled devices to interface with an RS485 soil sensor, collect environmental data, and transmit it to a remote TCP server.
Purpose: Facilitates real-time monitoring of soil parameters including temperature, humidity, EC, pH, nitrogen, phosphorus, potassium, and salinity.

Features

Sensor Communication: Interfaces with an RS485 soil sensor via UART using the Modbus protocol.
TCP Data Transmission: Sends sensor data and device login packets over a persistent TCP connection.
Timestamp Integration: Embeds BCD-encoded timestamps (YYMMddhhmmss) in data packets.
Robust Error Handling: Manages network and connection failures with automatic retries.
Logging: Provides detailed console output for debugging and monitoring.

Requirements

Hardware:
QuecPython-compatible microcontroller (e.g., Quectel module).
RS485 soil sensor connected to UART2 (default).


Software:
MicroPython with QuecPython extensions.
Required libraries: log, checkNet, utime, _thread, queue, usocket, machine.



Configuration

Editable Parameters:
PROJECT_NAME: "QuecPython_RS485_SoilSensor_TCP"
PROJECT_VERSION: "1.0.0"
IMEI: 15-digit device IMEI (e.g., "862942071230965")
TCP_SERVER_IP: Server IP address (e.g., "13.126.118.139")
TCP_SERVER_PORT: Server port (e.g., 9619)



Code Structure

Utility Functions:
get_timestamp_bytes(): Generates a 6-byte BCD timestamp.
build_login_packet(imei): Constructs a login packet with BCD-encoded IMEI.


SoilSensorUART Class:
Initializes UART for Modbus communication.
Sends queries and decodes sensor responses.
Formats sensor data into a structured packet.


TCP Handler:
persistent_tcp_send(): Manages TCP connections, sends login packets, and transmits sensor data.


Main Execution:
Ensures network connectivity, initializes the sensor, and starts the TCP communication loop.



Packet Formats

Login Packet:
Start Byte: 0x78
Protocol Index: 0x01
IMEI: 8 bytes (BCD-encoded, padded)
End Byte: 0x79


Sensor Data Packet:
Start Byte: 0x78
Protocol Index: 0x02
Timestamp: 6 bytes (BCD)
Sensor Data: 16 bytes (2 bytes per parameter)
End Byte: 0x79



Installation and Usage

Setup:
Connect the RS485 soil sensor to UART2.
Update configuration constants in the code.
Deploy the code to a QuecPython device.


Operation:
Waits for network connectivity.
Initializes the soil sensor.
Establishes a TCP connection and sends a login packet.
Queries the sensor every 30 seconds and transmits data.


Monitoring: Check console output for sensor readings and connection status.

Error Handling

Network: Retries connection if the network is unavailable.
TCP: Reconnects every 5 seconds on failure.
Sensor: Retries up to 5 times for valid data, skips cycle if unsuccessful.

Debugging

Logging: Uses log module at INFO level.
Output: Displays sensor values, TCP status, and Modbus response errors.
Tools: Monitor via serial console for real-time diagnostics.

Notes

Sensor Compatibility: Requires a soil sensor responding to the Modbus query 0x01 0x03 0x00 0x00 0x00 0x08 0x44 0x0C.
Server Setup: Ensure the TCP server accepts the specified packet formats.
Hardware: Verify stable power and correct RS485 wiring.

License

Terms: Provided as-is for development and evaluation purposes.
Warranty: No implied or expressed warranties.



