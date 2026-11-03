#!/usr/bin/env python3
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 1000

data = {
    "cpu_percent": np.clip(np.random.normal(18, 5, n_samples), 1, 60),
    "mem_percent": np.clip(np.random.normal(35, 6, n_samples), 10, 70),
    "data_usage_percent": np.clip(np.random.normal(25, 4, n_samples), 5, 65),
    "logs_usage_percent": np.clip(np.random.normal(20, 3, n_samples), 5, 60),
    "io_reads": np.clip(np.random.normal(1200, 200, n_samples), 100, 5000),
    "io_writes": np.clip(np.random.normal(800, 150, n_samples), 50, 4000)
}

df = pd.DataFrame(data)
df.to_csv("/opt/aimon/data/baseline_training.csv", index=False)
print("Synthetic normal baseline generated: 1,000 samples.")
