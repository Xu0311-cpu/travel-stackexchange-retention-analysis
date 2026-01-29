import os
import math
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY_PATH = os.path.join(PROJECT_ROOT, "data", "day8_travel_view_comment_summary.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day8_travel_view_comment_agg_ci.png")


def wilson_ci(k, n, z=1.96):
    """Wilson score interval for proportion."""
    if n == 0:
        return (None, None)
    p = k / n
    denom = 1 + (z**2)/n
    center = (p + (z**2)/(2*n)) / denom
    half = (z * math.sqrt((p*(1-p) + (z**2)/(4*n)) / n)) / denom
    return (center - half, center + half)


def main():
    df = pd.read_csv(SUMMARY_PATH)

    a = df[df["group"] == "view_only"].iloc[0]
    b = df[df["group"] == "view_comment"].iloc[0]

    a_n, a_k, a_p = int(a["total_base"]), int(a["total_returned"]), float(a["agg_rate"])
    b_n, b_k, b_p = int(b["total_base"]), int(b["total_returned"]), float(b["agg_rate"])

    a_low, a_high = wilson_ci(a_k, a_n)
    b_low, b_high = wilson_ci(b_k, b_n)

    labels = ["view-only", "view+comment"]
    vals = [a_p, b_p]
    yerr_low = [a_p - a_low, b_p - b_low]
    yerr_high = [a_high - a_p, b_high - b_p]

    plt.figure()
    plt.bar(labels, vals)
    plt.errorbar(labels, vals, yerr=[yerr_low, yerr_high], fmt="none", capsize=6)
    plt.title("Travel next-day return: view-only vs view+comment (agg with 95% CI)")
    plt.ylabel("Next-day return rate (aggregated)")
    plt.tight_layout()
    plt.savefig(OUT_FIG)
    plt.close()

    print("[OK] Saved figure:", OUT_FIG)
    print(f"view-only CI      : [{a_low:.3f}, {a_high:.3f}] (n={a_n})")
    print(f"view+comment CI   : [{b_low:.3f}, {b_high:.3f}] (n={b_n})")


if __name__ == "__main__":
    main()
