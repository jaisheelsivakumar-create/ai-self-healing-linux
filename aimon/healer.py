#!/usr/bin/env python3
import os
import subprocess
import time
import joblib
import pandas as pd
import psutil
from datetime import datetime

MODEL_PATH = "/opt/aimon/models/isolation_forest.joblib"
LOG_FILE = "/srv/logs/healer.log"

def log(msg):
    entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def heal_storage():
    log("ALERT: Storage anomaly detected! Initiating automated self-healing...")
    try:
        # Check free space left in volume group
        vg_check = subprocess.run(
            ["sudo", "vgs", "--noheadings", "-o", "vg_free", "vg_data"],
            capture_output=True, text=True, check=True
        )
        log(f"Available pool capacity in vg_data: {vg_check.stdout.strip()}")
        
        # Self-heal action: Expand lv_data by 1GB and resize XFS online
        log("Executing: lvextend -L +1G /dev/vg_data/lv_data && xfs_growfs /srv/data")
        subprocess.run(["sudo", "lvextend", "-L", "+1G", "/dev/vg_data/lv_data"], check=True)
        subprocess.run(["sudo", "xfs_growfs", "/srv/data"], check=True)
        log("SUCCESS: Storage volume lv_data safely extended online.")
    except subprocess.CalledProcessError as e:
        log(f"ERROR: Self-healing execution failed: {e}")

def monitor_and_heal():
    if not os.path.exists(MODEL_PATH):
        log(f"ERROR: Model file {MODEL_PATH} not found.")
        return

    model = joblib.load(MODEL_PATH)
    log("AI Self-Healing Engine initialized and monitoring live metrics.")

    # Collect current real-time metrics
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    data_disk = psutil.disk_usage('/srv/data').percent if os.path.exists('/srv/data') else 0.0
    logs_disk = psutil.disk_usage('/srv/logs').percent if os.path.exists('/srv/logs') else 0.0

    current_data = pd.DataFrame([{
        "cpu_percent": cpu,
        "mem_percent": mem,
        "data_usage_percent": data_disk,
        "logs_usage_percent": logs_disk
    }])

    # Predict anomaly (-1 indicates anomaly, 1 indicates normal behavior)
    prediction = model.predict(current_data)[0]
    log(f"Current Metrics: Data Disk={data_disk}%, Logs Disk={logs_disk}%, CPU={cpu}%, Memory={mem}% | Anomaly Prediction={prediction}")

    # Trigger healing if Isolation Forest flags an anomaly or usage spikes above 75%
    if prediction == -1 or data_disk > 75.0:
        heal_storage()
    else:
        log("Status: Normal operations. No remediation needed.")

if __name__ == "__main__":
    monitor_and_heal()
