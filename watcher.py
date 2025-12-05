import time
import os
import subprocess
import json
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "watcher.log")
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
def check_service(x):
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', x],
            capture_output=True,
            text=True
        )
        is_active = result.stdout.strip() == 'active'
        if not is_active:
            log(f"Service {x} is not active. Status: {result.stdout.strip()}")
        return is_active
    except Exception as e:
        log(f"Error checking service {x}: {str(e)}")
        return False

def restart_service(s):
    try:
        log(f"Restarting service {s}...")
        result = subprocess.run(
            ["systemctl", "restart", s],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log(f"Successfully restarted {s}")
            return True
        else:
            log(f"Failed to restart {s}: {result.stderr.strip()}")
            return False
    except Exception as e:
        log(f"Error restarting service {s}: {str(e)}")
        return False

def main():
    try:
        config = load_config()
        interval = config["interval"]
        services = config["services"]
        
        log("Watcher started...")
        log(f"Monitoring services: {', '.join(services)}")
        log(f"Check interval: {interval} seconds")
        
        while True:
            log("Checking services...")
            for service in services:
                if not check_service(service):
                    restart_service(service)
            time.sleep(interval)
    except FileNotFoundError:
        log("ERROR: config.json not found")
    except KeyError as e:
        log(f"ERROR: Missing key in config.json: {str(e)}")
    except Exception as e:
        log(f"ERROR: {str(e)}")
        raise

if __name__ == "__main__":
    main()