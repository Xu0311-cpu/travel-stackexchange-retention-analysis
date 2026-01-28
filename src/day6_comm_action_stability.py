import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "data", "day6_comm_action_stability.csv")


def users_in(df, day, community, action=None):
    d = df[df["event_date"] == day]
    d = d[d["community"] == community]
    if action is not None:
        d = d[d["action"] == action]
    return set(d["user_id"].unique())


def daily_d1_series(df, community, action):
    days = sorted(df["event_date"].unique())
    vals = []

    for i in range(len(days) - 1):
        d0, d1 = days[i], days[i + 1]
        base = users_in(df, d0, community, action)
        ret = users_in(df, d1, community, None)
        if len(base) >= 5:  # 控制极小样本
            vals.append(len(base & ret) / len(base))

    return vals


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    communities = sorted(df["community"].unique())
    actions = sorted(df["action"].unique())

    rows = []
    for c in communities:
        for a in actions:
            series = daily_d1_series(df, c, a)
            if len(series) < 5:
                continue
            rows.append([
                c, a,
                len(series),
                np.mean(series),
                np.std(series),
                np.percentile(series, 75) - np.percentile(series, 25)
            ])

    out = pd.DataFrame(
        rows,
        columns=["community", "action", "n_days", "avg_d1", "std_d1", "iqr_d1"]
    )

    out.to_csv(OUT_PATH, index=False)
    print("[OK] Saved:", OUT_PATH)
    print(out.sort_values("std_d1", ascending=False).head(10).to_string(index=False))


if __name__ == "__main__":
    main()
