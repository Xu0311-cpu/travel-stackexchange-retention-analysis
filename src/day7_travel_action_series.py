import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_SERIES = os.path.join(PROJECT_ROOT, "data", "day7_travel_action_daily_series.csv")
OUT_SUMMARY = os.path.join(PROJECT_ROOT, "data", "day7_travel_action_summary.csv")

TRAVEL = "travel"
ACTIONS_FOCUS = ["comment", "post", "like", "view"]


def users_in(df, day, community, action=None):
    d = df[df["event_date"] == day]
    d = d[d["community"] == community]
    if action is not None:
        d = d[d["action"] == action]
    return set(d["user_id"].unique())


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    # 只看 travel
    df_t = df[df["community"] == TRAVEL].copy()
    days = sorted(df_t["event_date"].unique())

    rows = []
    # 日序列：对每个 action，每个日期对(d->d+1)，算 base/returned/d1
    for a in ACTIONS_FOCUS:
        for i in range(len(days) - 1):
            d0, d1 = days[i], days[i + 1]
            base = users_in(df_t, d0, TRAVEL, action=a)
            nxt_any = users_in(df_t, d1, TRAVEL, action=None)

            base_n = len(base)
            ret_n = len(base & nxt_any)
            d1_ret = (ret_n / base_n) if base_n > 0 else None

            rows.append([d0, a, base_n, ret_n, d1_ret])

    series = pd.DataFrame(rows, columns=["date", "action", "base", "returned", "d1_retention"])
    series.to_csv(OUT_SERIES, index=False)

    # 汇总：看每个 action 的样本规模与稳定性（不设阈值，先全看）
    summary = (series[series["base"] > 0]
               .groupby("action")
               .agg(
                    days=("date", "count"),
                    total_base=("base", "sum"),
                    avg_base=("base", "mean"),
                    median_base=("base", "median"),
                    min_base=("base", "min"),
                    max_base=("base", "max"),
                    days_base_lt5=("base", lambda x: int((x < 5).sum())),
                    days_base_lt10=("base", lambda x: int((x < 10).sum())),
                    agg_d1=("returned", "sum")
               )
               .reset_index())

    # agg_d1 这里先存“returned 总数”，再算真正的 aggregated D1
    returned_sum = series.groupby("action")["returned"].sum().reset_index().rename(columns={"returned": "total_returned"})
    summary = summary.merge(returned_sum, on="action", how="left")
    summary["agg_d1_retention"] = summary["total_returned"] / summary["total_base"]

    # 加上“日均 D1”的均值/波动（只在 base>0 的天上计算）
    d1_stats = (series[series["base"] > 0]
                .groupby("action")["d1_retention"]
                .agg(avg_d1="mean", std_d1="std")
                .reset_index())
    summary = summary.merge(d1_stats, on="action", how="left")

    summary.to_csv(OUT_SUMMARY, index=False)

    print("[OK] Saved:")
    print(" -", OUT_SERIES)
    print(" -", OUT_SUMMARY)

    print("\n=== Travel action summary (key) ===")
    print(summary.sort_values("agg_d1_retention", ascending=False)[
        ["action", "total_base", "total_returned", "agg_d1_retention",
         "avg_base", "median_base", "min_base", "max_base",
         "days_base_lt5", "days_base_lt10", "avg_d1", "std_d1"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
