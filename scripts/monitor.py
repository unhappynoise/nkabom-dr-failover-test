import requests
import time
import subprocess
import datetime

PRIMARY_HEALTH_URL = "http://10.10.10.10:5000/health"
DR_IP = "10.10.20.10"
PRIMARY_IP = "10.10.10.10"
DNSMASQ_CONF = "/etc/dnsmasq.conf"
DOMAIN = "app.nkabom.internal"
LOG_FILE = "/home/primarysite/failover/failover.log"
FLAG_FILE = "/home/primarysite/failover/DR_IS_PRIMARY.flag"

CHECK_INTERVAL = 5
FAILURE_THRESHOLD = 3
TIMEOUT = 3

current_target = PRIMARY_IP
consecutive_failures = 0

def log(message):
    timestamp = datetime.datetime.now().isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_primary_health():
    try:
        response = requests.get(PRIMARY_HEALTH_URL, timeout=TIMEOUT)
        return response.status_code == 200
    except Exception:
        return False

def set_failover_flag():
    with open(FLAG_FILE, "w") as f:
        f.write(f"Failover occurred at {datetime.datetime.now().isoformat()}\n")
        f.write("DR site is now the authoritative primary.\n")
        f.write("DO NOT restart primarysite's PostgreSQL without re-cloning it as a new standby first.\n")

def update_dns(target_ip):
    with open(DNSMASQ_CONF, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith(f"address=/{DOMAIN}/"):
            new_lines.append(f"address=/{DOMAIN}/{target_ip}\n")
        else:
            new_lines.append(line)

    with open(DNSMASQ_CONF, "w") as f:
        f.writelines(new_lines)

    subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)

def main():
    global current_target, consecutive_failures
    log(f"Monitor started. Watching {PRIMARY_HEALTH_URL}. Current DNS target: {current_target}")

    while True:
        healthy = check_primary_health()

        if healthy:
            if consecutive_failures > 0:
                log(f"Primary health check recovered after {consecutive_failures} failures.")
            consecutive_failures = 0

            if current_target != PRIMARY_IP:
                log("Primary is healthy again, but staying on DR (manual failback required).")

        else:
            consecutive_failures += 1
            log(f"Primary health check FAILED ({consecutive_failures}/{FAILURE_THRESHOLD})")

            if consecutive_failures >= FAILURE_THRESHOLD and current_target != DR_IP:
                log(f"THRESHOLD REACHED. Initiating failover to DR ({DR_IP}).")
                update_dns(DR_IP)
                set_failover_flag()
                current_target = DR_IP
                log(f"FAILOVER COMPLETE. {DOMAIN} now points to {DR_IP}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
