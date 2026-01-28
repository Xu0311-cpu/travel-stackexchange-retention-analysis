import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "data", "day6_comm_action_stability_plus_base.csv")


def users_in(df, day, community, action=None):
    d = df[df["event_date"] == day]
    d = d[d["community"] == community]
    if action is not None:
        d = d[d["action"] == action]
    return set(d["user_id"].unique())


def daily_series_with_base(df, community, action, min_base=5):
    """
    对每个相邻日期对 (d -> d+1):
      base = 当天在该社区做该行为的用户数
      returned = base 中在次日仍出现在同社区(任意行为)的用户数
      d1 = returned/base
    只保留 base>=min_base 的天（避免极小样本把比例抖爆）
    """
    days = sorted(df["event_date"].unique())
    d1_list = []
    base_list = []
    ret_list = []

    for i in range(len(days) - 1):
        d0, d1 = days[i], days[i + 1]
        base = users_in(df, d0, community, action)
        nxt = users_in(df, d1, community, None)
        b = len(base)
        r = len(base & nxt)
        if b >= min_base:
            d1_list.append(r / b)
            base_list.append(b)
            ret_list.append(r)

    return d1_list, base_list, ret_list


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    communities = sorted(df["community"].unique())
    actions = sorted(df["action"].unique())

    rows = []
    for c in communities:
        for a in actions:
            d1_list, base_list, ret_list = daily_series_with_base(df, c, a, min_base=5)
            if len(d1_list) < 5:
                continue

            d1_arr = np.array(d1_list, dtype=float)
            base_arr = np.array(base_list, dtype=int)
            ret_arr = np.array(ret_list, dtype=int)

            rows.append([
                c, a,
                len(d1_arr),
                float(np.mean(d1_arr)),
                float(np.std(d1_arr)),
                float(np.percentile(d1_arr, 75) - np.percentile(d1_arr, 25)),
                int(np.sum(base_arr)),
                int(np.sum(ret_arr)),
                float(np.sum(ret_arr) / np.sum(base_arr)) if np.sum(base_arr) > 0 else np.nan,
                float(np.mean(base_arr)),
                float(np.median(base_arr)),
                int(np.min(base_arr)),
                int(np.max(base_arr)),
                int(np.sum(base_arr < 10)),
            ])

    out = pd.DataFrame(rows, columns=[
        "community", "action",
        "n_days",
        "avg_d1", "std_d1", "iqr_d1",
        "total_base", "total_returned", "agg_d1",
        "avg_base", "median_base", "min_base", "max_base",
        "days_base_lt10"
    ])

    out.to_csv(OUT_PATH, index=False)
    print("[OK] Saved:", OUT_PATH)

    # 1) 最“噪音嫌疑”：std高 + base偏小
    noise = out.sort_values(["std_d1", "avg_base"], ascending=[False, True]).head(10)
    print("\nTop 10 volatility candidates (high std, smaller base first):")
    print(noise.to_string(index=False))

    # 2) 最“可运营”：base够大 + std较小 + agg_d1不差
    reliable = out[(out["total_base"] >= 80) & (out["n_days"] >= 10)].copy()
    reliable = reliable.sort_values(["agg_d1", "std_d1"], ascending=[False, True]).head(10)
    print("\nTop 10 more reliable combos (enough base & days):")
    print(reliable.to_string(index=False))


if __name__ == "__main__":
    main()
