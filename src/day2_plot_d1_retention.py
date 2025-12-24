# src/day2_plot_d1_retention.py
from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_PATH = os.path.join(PROJECT_ROOT, "data", "day2_d1_retention.csv")
FIG_DIR = os.path.join(PROJECT_ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)
OUT_FIG = os.path.join(FIG_DIR, "day2_d1_retention.png")

d = pd.read_csv(IN_PATH)
d["date"] = pd.to_datetime(d["date"])

plt.figure()
plt.plot(d["date"], d["d1_retention"])
plt.title("Day2: D1 Retention (Toy Data)")
plt.xlabel("Date")
plt.ylabel("D1 retention")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(OUT_FIG, dpi=160)

print(f"[OK] Saved figure: {OUT_FIG}")
print(f"[INFO] Avg D1 retention: {d['d1_retention'].mean():.3f}")
print(f"[INFO] Min/Max: {d['d1_retention'].min():.3f} / {d['d1_retention'].max():.3f}")
