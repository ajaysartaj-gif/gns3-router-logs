import socket
import subprocess
from datetime import datetime

HOST = "0.0.0.0"
PORT = 514
LOG_FILE_NAME = "network_audit.log"

def push_to_github(raw_log):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_log = f"[{timestamp}] {raw_log.strip()}\n"
    
    # 1. Save to local log file
    with open(LOG_FILE_NAME, "a") as f:
        f.write(formatted_log)
    print("📝 Log saved locally")
    
    # 2. Push to GitHub
    try:
        subprocess.run(["git", "add", LOG_FILE_NAME], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Log sync"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("🚀 [GITHUB SYNC SUCCESS] Pushed to repo!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git error: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Initialize UDP Socket Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    server_socket.bind((HOST, PORT))
    print(f"=== Syslog Active on Port {PORT} ===")
    print("📋 Filter completely removed: Capturing ALL incoming terminal and routing traffic...")
    
    while True:
        # Buffer size handling large debug data sequences
        data, addr = server_socket.recvfrom(65535)
        decoded_log = data.decode('utf-8', errors='ignore').strip()
        
        # Display the incoming raw log stream in terminal console
        print(f"\n[{addr[0]}]: {decoded_log}")
        
        # Directly pass every packet to local append and Git sync functions
        push_to_github(decoded_log)

except PermissionError:
    print("❌ Run with sudo! (Port 514 requires administrative root privileges)")
except KeyboardInterrupt:
    print("\nStopping server...")
finally:
    server_socket.close()