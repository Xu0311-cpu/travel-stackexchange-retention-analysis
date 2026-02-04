import os
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY_PATH = os.path.join(PROJECT_ROOT, "data", "day9_travel_stratified_summary.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day9_travel_stratified_lift.png")

def main():
    df = pd.read_csv(SUMMARY_PATH)
    df = df.sort_values("bucket")

    labels = df["bucket"].tolist()
    lifts = df["lift"].tolist()

    plt.figure()
    plt.bar(labels, lifts)
    plt.axhline(0)
    plt.title("Travel: lift of view+comment vs view-only by activity bucket")
    plt.xlabel("Activity bucket (day0 events in travel)")
    plt.ylabel("Lift (B-A)")
    plt.tight_layout()
    plt.savefig(OUT_FIG)
    plt.close()

    print("[OK] Saved figure:", OUT_FIG)

if __name__ == "__main__":
    main()
