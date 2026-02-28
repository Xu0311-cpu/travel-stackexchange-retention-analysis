import os
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES_PATH = os.path.join(PROJECT_ROOT, "data", "day7_travel_action_daily_series.csv")

OUT_BASE = os.path.join(PROJECT_ROOT, "figures", "day7_travel_action_base_timeseries.png")
OUT_D1 = os.path.join(PROJECT_ROOT, "figures", "day7_travel_action_d1_timeseries.png")

ACTIONS_FOCUS = ["comment", "post", "like", "view"]

def main():
    df = pd.read_csv(SERIES_PATH)
    df["date"] = pd.to_datetime(df["date"])

    # ---- Plot base timeseries ----
    plt.figure()
    for a in ACTIONS_FOCUS:
        dfa = df[df["action"] == a].sort_values("date")
        plt.plot(dfa["date"], dfa["base"], label=a)

    plt.title("Travel: Base users by action (day-level)")
    plt.xlabel("Date")
    plt.ylabel("Base (users)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_BASE)
    plt.close()

    # ---- Plot D1 timeseries ----
    plt.figure()
    for a in ACTIONS_FOCUS:
        dfa = df[(df["action"] == a) & (df["base"] > 0)].sort_values("date")
        plt.plot(dfa["date"], dfa["d1_retention"], label=a)

    plt.title("Travel: D1 retention by action (day-level)")
    plt.xlabel("Date")
    plt.ylabel("D1 retention")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_D1)
    plt.close()

    print("[OK] Saved figures:")
    print(" -", OUT_BASE)
    print(" -", OUT_D1)

if __name__ == "__main__":
    main()
