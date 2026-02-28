import os
import numpy as np
import pandas as pd

# =====================
# Paths
# =====================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_STD = os.path.join(PROJECT_ROOT, "data", "day5_action_retention_standardized.csv")
OUT_CA = os.path.join(PROJECT_ROOT, "data", "day5_comm_action_agg.csv")


def users_in(df, day, community, action=None):
    d = df[df["event_date"] == day]
    d = d[d["community"] == community]
    if action is not None:
        d = d[d["action"] == action]
    return set(d["user_id"].unique())


def agg_retention_same_community_any_action(df, community, action):
    """
    base: users who did (community, action) on day d
    returned: those base users who appear in same community on day d+1 (any action)
    agg_d1 = sum(returned) / sum(base)
    """
    days = sorted(df["event_date"].unique())
    total_base = 0
    total_ret = 0

    for i in range(len(days) - 1):
        d0, d1 = days[i], days[i + 1]
        base = users_in(df, d0, community, action=action)
        ret_any = users_in(df, d1, community, action=None)

        total_base += len(base)
        total_ret += len(base & ret_any)

    if total_base == 0:
        return np.nan, 0, 0
    return total_ret / total_base, total_base, total_ret


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    communities = sorted(df["community"].unique())
    actions = sorted(df["action"].unique())

    # 1) 先算每个 community 的“标准权重”
    #    权重 = 这个社区在所有天里的总 base（每天社区的独立活跃用户数）
    days = sorted(df["event_date"].unique())
    comm_total_base = {c: 0 for c in communities}

    for i in range(len(days) - 1):
        d0 = days[i]
        for c in communities:
            base_comm = users_in(df, d0, c, action=None)
            comm_total_base[c] += len(base_comm)

    total_all = sum(comm_total_base.values())
    comm_weight = {c: (comm_total_base[c] / total_all if total_all > 0 else 0) for c in communities}

    # 2) 算 community×action 的 aggregated D1（和 Day4 类似，但统一输出一份表）
    rows = []
    for c in communities:
        for a in actions:
            r, tb, tr = agg_retention_same_community_any_action(df, c, a)
            rows.append([c, a, r, tb, tr])

    ca = pd.DataFrame(rows, columns=["community", "action", "agg_d1", "total_base", "total_returned"])
    ca.to_csv(OUT_CA, index=False)

    # 3) 做“标准化”：
    #    standardized(action) = Σ_c weight(c) * agg_d1(c, action)
    std_rows = []
    for a in actions:
        val = 0.0
        used_w = 0.0
        for c in communities:
            r = ca[(ca["community"] == c) & (ca["action"] == a)]["agg_d1"].values[0]
            w = comm_weight[c]
            if np.isnan(r):
                continue
            val += w * r
            used_w += w
        # 归一化：如果有些 community-action 没数据，避免权重缺口
        std = val / used_w if used_w > 0 else np.nan
        std_rows.append([a, std])

    std_df = pd.DataFrame(std_rows, columns=["action", "standardized_d1"])
    std_df.to_csv(OUT_STD, index=False)

    print("[OK] Saved:")
    print(" -", OUT_CA)
    print(" -", OUT_STD)
    print("\nStandardized D1 by action:")
    print(std_df.sort_values("standardized_d1", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
