import socket

# Bind to all available interfaces on the standard Syslog port
UDP_IP = "0.0.0.0"
UDP_PORT = 514

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind((UDP_IP, UDP_PORT))
    print(f"=== Mac Syslog Server Active. Listening on UDP port {UDP_PORT} ===")
except PermissionError:
    print("Error: You must run this script with 'sudo' to use port 514!")
    exit()

while True:
    data, addr = sock.recvfrom(1024)
    print(f"[{addr[0]}]: {data.decode('utf-8', errors='ignore').strip()}")
