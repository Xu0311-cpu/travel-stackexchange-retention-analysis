# src/day2_retention_d1.py
from __future__ import annotations
import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "data", "day2_d1_retention.csv")

df = pd.read_csv(EVENTS_PATH, usecols=["user_id", "event_date"])
df["event_date"] = pd.to_datetime(df["event_date"])

daily_sets = df.groupby("event_date")["user_id"].apply(lambda s: set(s.tolist())).to_dict()
dates = sorted(daily_sets.keys())

rows = []
for i in range(len(dates) - 1):
    d0, d1 = dates[i], dates[i + 1]
    s0, s1 = daily_sets[d0], daily_sets[d1]
    base = len(s0)
    if base == 0:
        continue
    returned = len(s0 & s1)
    d1_ret = returned / base
    rows.append(
        {
            "date": d0.date().isoformat(),
            "base_users": base,
            "returned_users": returned,
            "d1_retention": round(d1_ret, 3),
        }
    )

out = pd.DataFrame(rows)
out.to_csv(OUT_PATH, index=False)

print(f"[OK] Saved: {OUT_PATH}")
print(out.head(10).to_string(index=False))
print(f"[OK] Avg D1 retention: {out['d1_retention'].mean():.3f}")
