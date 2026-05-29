import socket
import subprocess
from datetime import datetime

# Configuration
HOST = "0.0.0.0"
PORT = 514
LOG_FILE_NAME = "network_audit.log"

def push_to_github(raw_log):
    """Appends logs to a local file and handles the automated Git push 
engine"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_log = f"[{timestamp}] {raw_log.strip()}\n"
    
    # 1. Append the new router alert to your tracking file
    with open(LOG_FILE_NAME, "a") as f:
        f.write(formatted_log)
        
    print(f"📝 Log saved locally to {LOG_FILE_NAME}")
    
    # 2. Programmatically push to your GitHub Repository
    try:
        # Run standard local Git operations sequentially
        subprocess.run(["git", "add", LOG_FILE_NAME], check=True, 
capture_output=True)
        subprocess.run(["git", "commit", "-m", "Automated Telemetry: 
Interface State Change"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, 
capture_output=True)
        print("🚀 [GITHUB SYNC SUCCESS] Live log pushed to your repository 
successfully!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git Push Skipped or Failed: 
{e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ System Error during Git sync: {str(e)}")

# Initialize Socket Listener
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    server_socket.bind((HOST, PORT))
    print("=============================================================")
    print(f"=== Mac Syslog Server Active. Listening on UDP port {PORT} 
===")
    print("=============================================================")
    
    while True:
        data, addr = server_socket.recvfrom(4096)
        decoded_log = data.decode('utf-8', errors='ignore')
        
        # Print to your local terminal screen
        print(f"\n[{addr[0]}]: {decoded_log.strip()}")
        
        # Filter for real interface or config changes before pushing
        if any(trigger in decoded_log for trigger in ["CHANGED", "UPDOWN", 
"DOWN", "CONFIG_I"]):
            push_to_github(decoded_log)
            
except PermissionError:
    print("❌ Error: You must run this script with 'sudo' to use port 
514!")
except KeyboardInterrupt:
    print("\nStopping Syslog Server safely...")
finally:
    server_socket.close()
