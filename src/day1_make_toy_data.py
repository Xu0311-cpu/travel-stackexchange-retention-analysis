# src/day1_make_toy_data.py
from __future__ import annotations
import os
import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(7)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUT_PATH = os.path.join(DATA_DIR, "toy_events.csv")

users = [f"u{str(i).zfill(3)}" for i in range(1, 81)]
start = datetime(2025, 12, 1)
days = 21
communities = ["games", "fitness", "food", "travel", "study", "tech"]
actions = ["view", "like", "comment", "post"]

rows = []
for day in range(days):
    date = start + timedelta(days=day)
    base_active = 18 + (6 if date.weekday() >= 5 else 0)  # weekend boost
    active_n = min(len(users), base_active + random.randint(-3, 5))
    active_users = random.sample(users, active_n)

    for u in active_users:
        n_events = random.randint(1, 8)
        for _ in range(n_events):
            act = random.choices(actions, weights=[55, 25, 15, 5], k=1)[0]
            community = random.choice(communities)
            content_type = random.choices(
                ["text", "image", "video"], weights=[55, 25, 20], k=1
            )[0]
            rows.append(
                {
                    "user_id": u,
                    "event_date": date.strftime("%Y-%m-%d"),
                    "community": community,
                    "content_type": content_type,
                    "action": act,
                }
            )

df = pd.DataFrame(rows)
df.to_csv(OUT_PATH, index=False)

print(f"[OK] Wrote {len(df):,} rows to: {OUT_PATH}")
print(df.head(5).to_string(index=False))
