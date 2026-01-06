import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

df = pd.read_csv(DATA_PATH)

# 全量：每天所有活跃用户（不分 action）
all_users_by_day = df.groupby("event_date")["user_id"].apply(set)
dates = sorted(all_users_by_day.keys())

actions = sorted(df["action"].unique())
results = []

for act in actions:
    df_a = df[df["action"] == act]
    users_by_day_act = df_a.groupby("event_date")["user_id"].apply(set)

    d1_list = []
    for i in range(len(dates) - 1):
        d0 = dates[i]
        d1 = dates[i + 1]

        base_users = users_by_day_act.get(d0, set())
        if len(base_users) == 0:
            continue

        returned_users = base_users & all_users_by_day[d1]
        d1_ret = len(returned_users) / len(base_users)
        d1_list.append(d1_ret)

    if d1_list:
        results.append({
            "action": act,
            "avg_d1_retention": round(sum(d1_list) / len(d1_list), 3),
            "n_days": len(d1_list)
        })

out_df = pd.DataFrame(results).sort_values("avg_d1_retention", ascending=False)
print("Avg D1 retention by action:")
print(out_df)

OUT_PATH = os.path.join(PROJECT_ROOT, "data", "day3_d1_retention_by_action.csv")
out_df.to_csv(OUT_PATH, index=False)
print(f"[OK] Saved: {OUT_PATH}")
