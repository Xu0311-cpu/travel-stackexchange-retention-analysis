import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_SUMMARY = os.path.join(PROJECT_ROOT, "data", "day10_l1_to_l2_transition.csv")

TRAVEL = "travel"

def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    df_t = df[df["community"] == TRAVEL].copy()
    days = sorted(df_t["event_date"].unique())

    rows = []

    for d in days:
        day_df = df_t[df_t["event_date"] == d]

        # 当天每个用户的事件数
        cnt = day_df.groupby("user_id").size().reset_index(name="n_events")

        # 只看 L1 用户
        l1_users = cnt[cnt["n_events"] == 1]["user_id"]

        for uid in l1_users:
            action = day_df[day_df["user_id"] == uid]["action"].iloc[0]

            # 是否当天升级到 2+（不会发生，但逻辑留着）
            upgraded_same_day = 0

            # 是否次日升级到 2+（在 travel）
            next_day = d + pd.Timedelta(days=1)
            next_df = df_t[df_t["event_date"] == next_day]
            upgraded_next_day = int(
                next_df[next_df["user_id"] == uid].shape[0] >= 2
            )

            rows.append([
                d, uid, action, upgraded_next_day
            ])

    out = pd.DataFrame(rows, columns=[
        "date", "user_id", "first_action", "upgraded_to_L2_next_day"
    ])

    summary = (out.groupby("first_action")
               .agg(
                   l1_users=("user_id", "nunique"),
                   upgraded=("upgraded_to_L2_next_day", "sum")
               )
               .reset_index())

    summary["upgrade_rate"] = summary["upgraded"] / summary["l1_users"]
    summary = summary.sort_values("upgrade_rate", ascending=False)

    summary.to_csv(OUT_SUMMARY, index=False)

    print("[OK] Saved:", OUT_SUMMARY)
    print("\n=== L1 → L2 upgrade by first action (travel) ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
