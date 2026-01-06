import os
import pandas as pd
import math

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

df = pd.read_csv(DATA_PATH)

# ===== Helper: Wilson CI for proportion (no heavy stats lib) =====
def wilson_ci(success: int, total: int, z: float = 1.96):
    if total == 0:
        return (None, None)
    phat = success / total
    denom = 1 + (z**2) / total
    center = (phat + (z**2) / (2 * total)) / denom
    margin = (z * math.sqrt((phat * (1 - phat) + (z**2) / (4 * total)) / total)) / denom
    return (center - margin, center + margin)

# ===== Build all-users-by-day (global activity) =====
all_users_by_day = df.groupby("event_date")["user_id"].apply(set)
dates = sorted(all_users_by_day.keys())
actions = sorted(df["action"].unique())
communities = sorted(df["community"].unique())

# -------------------------------------------------------------------
# (A) Action base size diagnostics: how big is the base for each action?
# -------------------------------------------------------------------
per_action_day_rows = []

for act in actions:
    df_a = df[df["action"] == act]
    base_users_by_day = df_a.groupby("event_date")["user_id"].apply(set)

    for i in range(len(dates) - 1):
        d0 = dates[i]
        d1 = dates[i + 1]

        base_users = base_users_by_day.get(d0, set())
        returned_users = base_users & all_users_by_day[d1]  # "returned" = active next day (any action)

        base_n = len(base_users)
        ret_n = len(returned_users)
        d1_ret = (ret_n / base_n) if base_n > 0 else None
        lo, hi = wilson_ci(ret_n, base_n)

        per_action_day_rows.append({
            "action": act,
            "date": d0,
            "base_users": base_n,
            "returned_users": ret_n,
            "d1_retention": None if d1_ret is None else round(d1_ret, 3),
            "ci_low": None if lo is None else round(lo, 3),
            "ci_high": None if hi is None else round(hi, 3),
        })

per_action_day = pd.DataFrame(per_action_day_rows)

# Summary base stats (this answers: "post is high because base is tiny?")
base_stats = (
    per_action_day
    .dropna(subset=["d1_retention"])
    .groupby("action")
    .agg(
        avg_base=("base_users", "mean"),
        median_base=("base_users", "median"),
        min_base=("base_users", "min"),
        max_base=("base_users", "max"),
        avg_d1=("d1_retention", "mean"),
        days=("date", "count"),
        days_base_lt5=("base_users", lambda s: int((s < 5).sum())),
        days_base_lt10=("base_users", lambda s: int((s < 10).sum())),
    )
    .reset_index()
)

# Aggregate retention per action across all days (more stable than averaging)
agg_rows = []
for act in actions:
    sub = per_action_day[(per_action_day["action"] == act) & per_action_day["d1_retention"].notna()]
    total_base = int(sub["base_users"].sum())
    total_ret = int(sub["returned_users"].sum())
    agg_ret = total_ret / total_base if total_base > 0 else None
    lo, hi = wilson_ci(total_ret, total_base)
    agg_rows.append({
        "action": act,
        "total_base": total_base,
        "total_returned": total_ret,
        "agg_d1_retention": None if agg_ret is None else round(agg_ret, 3),
        "agg_ci_low": None if lo is None else round(lo, 3),
        "agg_ci_high": None if hi is None else round(hi, 3),
    })

agg_action = pd.DataFrame(agg_rows).sort_values("agg_d1_retention", ascending=False)

print("\n=== Day4(A1) Base size + Avg D1 (mean-of-days) by action ===")
print(base_stats.sort_values("avg_d1", ascending=False))

print("\n=== Day4(A2) Aggregated D1 by action (more stable) ===")
print(agg_action)

# -------------------------------------------------------------------
# (B) Community × Action: does "post" drive retention inside specific communities?
# Definition:
#   base = users who did (action) in (community) on day t
#   returned = those users active in SAME community on day t+1 (any action)
# -------------------------------------------------------------------
comm_users_by_day = df.groupby(["community", "event_date"])["user_id"].apply(set)

rows = []
for comm in communities:
    for act in actions:
        df_ca = df[(df["community"] == comm) & (df["action"] == act)]
        base_users_by_day = df_ca.groupby("event_date")["user_id"].apply(set)

        vals = []
        total_base = 0
        total_ret = 0

        for i in range(len(dates) - 1):
            d0 = dates[i]
            d1 = dates[i + 1]

            base_users = base_users_by_day.get(d0, set())
            next_comm_users = comm_users_by_day.get((comm, d1), set())

            base_n = len(base_users)
            if base_n == 0:
                continue

            ret_n = len(base_users & next_comm_users)

            vals.append(ret_n / base_n)
            total_base += base_n
            total_ret += ret_n

        if vals:
            mean_ret = sum(vals) / len(vals)
            agg_ret = total_ret / total_base if total_base > 0 else None
            rows.append({
                "community": comm,
                "action": act,
                "avg_d1_retention": round(mean_ret, 3),
                "agg_d1_retention": None if agg_ret is None else round(agg_ret, 3),
                "days": len(vals),
                "total_base": total_base,
            })

comm_action = pd.DataFrame(rows).sort_values(["agg_d1_retention", "total_base"], ascending=[False, False])

print("\n=== Day4(B) Top 12 community×action by aggregated D1 (same-community next-day return) ===")
print(comm_action.head(12))

# Save outputs (data/ is ignored by git and that's OK)
OUT1 = os.path.join(PROJECT_ROOT, "data", "day4_action_day_table.csv")
OUT2 = os.path.join(PROJECT_ROOT, "data", "day4_action_base_stats.csv")
OUT3 = os.path.join(PROJECT_ROOT, "data", "day4_comm_action_retention.csv")

per_action_day.to_csv(OUT1, index=False)
base_stats.to_csv(OUT2, index=False)
comm_action.to_csv(OUT3, index=False)

print(f"\n[OK] Saved: {OUT1}")
print(f"[OK] Saved: {OUT2}")
print(f"[OK] Saved: {OUT3}")
