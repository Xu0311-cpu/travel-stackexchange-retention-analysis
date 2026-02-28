import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_FIG1 = os.path.join(PROJECT_ROOT, "figures", "day5_action_standardized_ci.png")
OUT_FIG2 = os.path.join(PROJECT_ROOT, "figures", "day5_comm_action_heatmap.png")


def users_in(df, day, community, action=None):
    d = df[df["event_date"] == day]
    d = d[d["community"] == community]
    if action is not None:
        d = d[d["action"] == action]
    return set(d["user_id"].unique())


def standardized_by_action_for_sample(df, days_sample):
    communities = sorted(df["community"].unique())
    actions = sorted(df["action"].unique())

    # community weights from sampled days (community base)
    comm_total = {c: 0 for c in communities}
    for i in range(len(days_sample) - 1):
        d0 = days_sample[i]
        for c in communities:
            comm_total[c] += len(users_in(df, d0, c, action=None))
    total_all = sum(comm_total.values())
    w = {c: (comm_total[c] / total_all if total_all > 0 else 0) for c in communities}

    # aggregated retention per community-action over sampled days
    result = {}
    for a in actions:
        val = 0.0
        used = 0.0
        for c in communities:
            total_base = 0
            total_ret = 0
            for i in range(len(days_sample) - 1):
                d0, d1 = days_sample[i], days_sample[i + 1]
                base = users_in(df, d0, c, action=a)
                ret_any = users_in(df, d1, c, action=None)
                total_base += len(base)
                total_ret += len(base & ret_any)
            r = (total_ret / total_base) if total_base > 0 else np.nan
            if np.isnan(r):
                continue
            val += w[c] * r
            used += w[c]
        result[a] = (val / used) if used > 0 else np.nan
    return result


def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
    days = sorted(df["event_date"].unique())

    # ===== Bootstrap CI over days =====
    rng = np.random.default_rng(42)
    B = 500
    actions = sorted(df["action"].unique())

    samples = {a: [] for a in actions}
    for _ in range(B):
        # sample days with replacement, keep sorted order
        sampled_days = sorted(rng.choice(days, size=len(days), replace=True))
        res = standardized_by_action_for_sample(df, sampled_days)
        for a in actions:
            if not np.isnan(res[a]):
                samples[a].append(res[a])

    rows = []
    for a in actions:
        arr = np.array(samples[a])
        mean = float(np.mean(arr))
        lo = float(np.quantile(arr, 0.025))
        hi = float(np.quantile(arr, 0.975))
        rows.append([a, mean, lo, hi])

    ci = pd.DataFrame(rows, columns=["action", "std_mean", "ci_low", "ci_high"]).sort_values("std_mean", ascending=False)

    # ===== Plot 1: standardized + CI =====
    plt.figure()
    x = np.arange(len(ci))
    y = ci["std_mean"].values
    yerr = np.vstack([y - ci["ci_low"].values, ci["ci_high"].values - y])

    plt.bar(ci["action"].values, y)
    plt.errorbar(ci["action"].values, y, yerr=yerr, fmt="none", capsize=4)
    plt.title("Standardized D1 Retention by Action (Bootstrap 95% CI)")
    plt.xlabel("Action")
    plt.ylabel("Standardized D1")
    plt.savefig(OUT_FIG1)
    plt.close()

    # ===== Plot 2: heatmap community x action (agg on full data) =====
    communities = sorted(df["community"].unique())
    heat = np.zeros((len(communities), len(actions)), dtype=float)

    for i, c in enumerate(communities):
        for j, a in enumerate(actions):
            total_base = 0
            total_ret = 0
            for k in range(len(days) - 1):
                d0, d1 = days[k], days[k + 1]
                base = users_in(df, d0, c, action=a)
                ret_any = users_in(df, d1, c, action=None)
                total_base += len(base)
                total_ret += len(base & ret_any)
            heat[i, j] = (total_ret / total_base) if total_base > 0 else np.nan

    plt.figure()
    plt.imshow(heat, aspect="auto")
    plt.xticks(np.arange(len(actions)), actions)
    plt.yticks(np.arange(len(communities)), communities)
    plt.title("Community × Action Aggregated D1 (same community next-day return)")
    plt.xlabel("Action")
    plt.ylabel("Community")
    plt.colorbar()
    plt.savefig(OUT_FIG2)
    plt.close()

    print("[OK] Saved figures:")
    print(" -", OUT_FIG1)
    print(" -", OUT_FIG2)
    print("\nStandardized D1 (mean + 95% CI):")
    print(ci.to_string(index=False))


if __name__ == "__main__":
    main()
