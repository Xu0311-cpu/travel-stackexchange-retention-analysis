# src/day1_plot_dau.py
from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAU_PATH = os.path.join(PROJECT_ROOT, "data", "day1_dau.csv")
FIG_DIR = os.path.join(PROJECT_ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)
OUT_FIG = os.path.join(FIG_DIR, "day1_dau.png")

dau = pd.read_csv(DAU_PATH)
dau["event_date"] = pd.to_datetime(dau["event_date"])

plt.figure()
plt.plot(dau["event_date"], dau["dau"])
plt.title("Day1: Daily Active Users (Toy Community Data)")
plt.xlabel("Date")
plt.ylabel("DAU")
plt.tight_layout()
plt.savefig(OUT_FIG, dpi=160)

print(f"[OK] Saved figure: {OUT_FIG}")
