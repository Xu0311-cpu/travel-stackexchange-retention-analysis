import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

df = pd.read_csv(DATA_PATH)
communities = df["community"].unique()
print(df.head())

# 先只看一个 community，比如 fitness
#comm = "fitness"
#df_c = df[df["community"] == comm]

# 看看 fitness 社区在不同日期有哪些用户
#users_by_day = df_c.groupby("event_date")["user_id"].apply(set)

#print("\nUsers by day (example: fitness):")
#for day, users in list(users_by_day.items())[:3]:
#    print(day, users)

results = []

for comm in communities:
    df_c = df[df["community"] == comm]
    users_by_day = df_c.groupby("event_date")["user_id"].apply(set)

    dates = sorted(users_by_day.keys())
    d1_values = []

    for i in range(len(dates) - 1):
        users_d0 = users_by_day[dates[i]]
        users_d1 = users_by_day[dates[i + 1]]

        if len(users_d0) == 0:
            continue

        retention = len(users_d0 & users_d1) / len(users_d0)
        d1_values.append(retention)

    if d1_values:
        avg_d1 = sum(d1_values) / len(d1_values)
        results.append({
            "community": comm,
            "avg_d1_retention": round(avg_d1, 3)
        })


# ===== Step: compute D1 retention for one community =====
dates = list(users_by_day.keys())
dates.sort()

print("\nD1 retention for fitness:")
for i in range(len(dates) - 1):
    d0 = dates[i]
    d1 = dates[i + 1]

    users_d0 = users_by_day[d0]
    users_d1 = users_by_day[d1]

    returned = users_d0 & users_d1
    retention = len(returned) / len(users_d0)

    print(f"{d0} -> {d1}: base={len(users_d0)}, returned={len(returned)}, D1={retention:.3f}")

result_df = pd.DataFrame(results).sort_values("avg_d1_retention", ascending=False)
print("\nAvg D1 retention by community:")
print(result_df)

OUT_PATH = os.path.join(PROJECT_ROOT, "data", "day2_d1_retention_by_community.csv")
result_df.to_csv(OUT_PATH, index=False)
print(f"\n[OK] Saved: {OUT_PATH}")
