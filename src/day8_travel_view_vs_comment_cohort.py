import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_DAILY = os.path.join(PROJECT_ROOT, "data", "day8_travel_view_comment_daily.csv")
OUT_SUMMARY = os.path.join(PROJECT_ROOT, "data", "day8_travel_view_comment_summary.csv")

TRAVEL = "travel"


def users(df, day, action=None):
    d = df[df["event_date"] == day]
    d = d[d["community"] == TRAVEL]
    if action is not None:
        d = d[d["action"] == action]
    return set(d["user_id"].unique())


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    df_t = df[df["community"] == TRAVEL].copy()
    days = sorted(df_t["event_date"].unique())

    rows = []
    for i in range(len(days) - 1):
        d0, d1 = days[i], days[i + 1]

        view_users = users(df_t, d0, action="view")
        comment_users = users(df_t, d0, action="comment")
        next_day_any = users(df_t, d1, action=None)

        group_b = view_users & comment_users          # view+comment
        group_a = view_users - group_b                # view-only

        a_base = len(group_a)
        b_base = len(group_b)

        a_ret = len(group_a & next_day_any)
        b_ret = len(group_b & next_day_any)

        a_rate = (a_ret / a_base) if a_base > 0 else None
        b_rate = (b_ret / b_base) if b_base > 0 else None

        lift = (b_rate - a_rate) if (a_rate is not None and b_rate is not None) else None
        ratio = (b_rate / a_rate) if (a_rate not in [None, 0] and b_rate is not None) else None

        rows.append([
            d0,
            a_base, a_ret, a_rate,
            b_base, b_ret, b_rate,
            lift, ratio
        ])

    daily = pd.DataFrame(rows, columns=[
        "date",
        "view_only_base", "view_only_returned", "view_only_rate",
        "view_comment_base", "view_comment_returned", "view_comment_rate",
        "lift", "ratio"
    ])

    daily.to_csv(OUT_DAILY, index=False)

    # aggregated（更稳）
    a_base_total = int(daily["view_only_base"].sum())
    a_ret_total = int(daily["view_only_returned"].sum())
    b_base_total = int(daily["view_comment_base"].sum())
    b_ret_total = int(daily["view_comment_returned"].sum())

    a_agg = (a_ret_total / a_base_total) if a_base_total > 0 else None
    b_agg = (b_ret_total / b_base_total) if b_base_total > 0 else None
    lift_agg = (b_agg - a_agg) if (a_agg is not None and b_agg is not None) else None
    ratio_agg = (b_agg / a_agg) if (a_agg not in [None, 0] and b_agg is not None) else None

    summary = pd.DataFrame([{
        "group": "view_only",
        "total_base": a_base_total,
        "total_returned": a_ret_total,
        "agg_rate": a_agg
    }, {
        "group": "view_comment",
        "total_base": b_base_total,
        "total_returned": b_ret_total,
        "agg_rate": b_agg
    }, {
        "group": "comparison",
        "total_base": a_base_total + b_base_total,
        "total_returned": a_ret_total + b_ret_total,
        "agg_rate": None,
        "lift_agg": lift_agg,
        "ratio_agg": ratio_agg
    }])

    summary.to_csv(OUT_SUMMARY, index=False)

    print("[OK] Saved:")
    print(" -", OUT_DAILY)
    print(" -", OUT_SUMMARY)

    print("\n=== Aggregated comparison (travel) ===")
    print(f"view-only   : base={a_base_total}, returned={a_ret_total}, rate={a_agg:.3f}" if a_agg is not None else "view-only: N/A")
    print(f"view+comment: base={b_base_total}, returned={b_ret_total}, rate={b_agg:.3f}" if b_agg is not None else "view+comment: N/A")
    if lift_agg is not None:
        print(f"lift (B-A)  : {lift_agg:.3f}")
    if ratio_agg is not None:
        print(f"ratio (B/A) : {ratio_agg:.3f}")

    # 给你一个“肉眼可读”的前几天
    print("\n=== First 10 daily rows (sanity check) ===")
    print(daily.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
