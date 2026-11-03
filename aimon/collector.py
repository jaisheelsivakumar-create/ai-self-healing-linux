import os
import psutil
import pandas as pd
from datetime import datetime

METRICS_FILE = "/opt/aimon/data/metrics.csv"

def collect_metrics():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()

    data_disk = psutil.disk_usage('/srv/data').percent if os.path.exists('/srv/data') else 0.0
    logs_disk = psutil.disk_usage('/srv/logs').percent if os.path.exists('/srv/logs') else 0.0

    io_counters = psutil.disk_io_counters()
    read_count = io_counters.read_count if io_counters else 0
    write_count = io_counters.write_count if io_counters else 0

    return {
        "timestamp": timestamp,
        "cpu_percent": cpu_percent,
        "mem_percent": mem.percent,
        "data_usage_percent": data_disk,
        "logs_usage_percent": logs_disk,
        "io_reads": read_count,
        "io_writes": write_count
    }

def main():
    metric = collect_metrics()
    df = pd.DataFrame([metric])

    header = not os.path.exists(METRICS_FILE)
    df.to_csv(METRICS_FILE, mode='a', index=False, header=header)
    print(f"[{metric['timestamp']}] Recorded: Data={metric['data_usage_percent']}%, Logs={metric['logs_usage_percent']}%, CPU={metric['cpu_percent']}%")

if __name__ == "__main__":
    main()
