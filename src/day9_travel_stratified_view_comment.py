import os
import math
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_DAILY = os.path.join(PROJECT_ROOT, "data", "day9_travel_stratified_view_comment.csv")
OUT_SUMMARY = os.path.join(PROJECT_ROOT, "data", "day9_travel_stratified_summary.csv")

TRAVEL = "travel"


def bucket_events(n_events: int) -> str:
    if n_events <= 1:
        return "L1_1event"
    elif n_events == 2:
        return "L2_2events"
    else:
        return "L3_3plus"


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + (z**2)/n
    center = (p + (z**2)/(2*n)) / denom
    half = (z * math.sqrt((p*(1-p) + (z**2)/(4*n)) / n)) / denom
    return (center - half, center + half)


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    df_t = df[df["community"] == TRAVEL].copy()
    days = sorted(df_t["event_date"].unique())

    rows = []

    for i in range(len(days) - 1):
        d0, d1 = days[i], days[i + 1]

        day0 = df_t[df_t["event_date"] == d0].copy()
        day1 = df_t[df_t["event_date"] == d1].copy()

        # 当天每个用户的 event 数（活跃度 proxy）
        user_events = (day0.groupby("user_id")
                       .size()
                       .reset_index(name="n_events"))
        user_events["bucket"] = user_events["n_events"].apply(bucket_events)

        # 当天是否 view / 是否 comment
        user_flags = (day0.groupby("user_id")
                      .agg(
                          did_view=("action", lambda x: int((x == "view").any())),
                          did_comment=("action", lambda x: int((x == "comment").any()))
                      )
                      .reset_index())

        # 合并活跃度层
        u = user_events.merge(user_flags, on="user_id", how="left").fillna(0)

        # 次日是否回到 travel（任意行为）
        next_users = set(day1["user_id"].unique())
        u["returned_next_day"] = u["user_id"].apply(lambda x: int(x in next_users))

        # 只关注“view 过的人”，再分 view-only vs view+comment
        u = u[u["did_view"] == 1].copy()
        u["group"] = np.where(u["did_comment"] == 1, "view_comment", "view_only")

        # 每个 bucket×group 做统计
        g = (u.groupby(["bucket", "group"])
             .agg(
                 base=("user_id", "nunique"),
                 returned=("returned_next_day", "sum")
             )
             .reset_index())
        g["date"] = d0
        g["rate"] = g["returned"] / g["base"]

        rows.append(g)

    daily = pd.concat(rows, ignore_index=True)

    # 保存 daily
    daily.to_csv(OUT_DAILY, index=False)

    # aggregated summary：每层内汇总 base/returned，算 agg rate + CI
    agg = (daily.groupby(["bucket", "group"])
           .agg(total_base=("base", "sum"), total_returned=("returned", "sum"))
           .reset_index())
    agg["agg_rate"] = agg["total_returned"] / agg["total_base"]
    agg[["ci_low", "ci_high"]] = agg.apply(
        lambda r: pd.Series(wilson_ci(int(r["total_returned"]), int(r["total_base"]))),
        axis=1
    )

    # pivot 成对照：每个 bucket 一行，带 lift/ratio
    a = agg[agg["group"] == "view_only"].rename(columns={
        "total_base": "a_base", "total_returned": "a_ret", "agg_rate": "a_rate",
        "ci_low": "a_ci_low", "ci_high": "a_ci_high"
    })
    b = agg[agg["group"] == "view_comment"].rename(columns={
        "total_base": "b_base", "total_returned": "b_ret", "agg_rate": "b_rate",
        "ci_low": "b_ci_low", "ci_high": "b_ci_high"
    })

    summary = a.merge(b, on="bucket", how="outer")
    summary["lift"] = summary["b_rate"] - summary["a_rate"]
    summary["ratio"] = summary["b_rate"] / summary["a_rate"]

    summary.to_csv(OUT_SUMMARY, index=False)

    print("[OK] Saved:")
    print(" -", OUT_DAILY)
    print(" -", OUT_SUMMARY)

    print("\n=== Stratified aggregated comparison (travel, view users only) ===")
    cols = ["bucket",
            "a_base", "a_ret", "a_rate", "a_ci_low", "a_ci_high",
            "b_base", "b_ret", "b_rate", "b_ci_low", "b_ci_high",
            "lift", "ratio"]
    print(summary[cols].sort_values("bucket").to_string(index=False))


if __name__ == "__main__":
    main()
