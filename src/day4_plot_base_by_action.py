import os
import pandas as pd
import matplotlib.pyplot as plt

# ===== paths =====
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "day4_action_base_stats.csv")
FIG_PATH = os.path.join(PROJECT_ROOT, "figures", "day4_avg_base_by_action.png")

# ===== load data =====
df = pd.read_csv(DATA_PATH)

# ===== plot =====
plt.figure()
plt.bar(df["action"], df["avg_base"])
plt.title("Average Daily Base Size by Action")
plt.xlabel("Action")
plt.ylabel("Average Daily Base Users")

# ===== save =====
plt.savefig(FIG_PATH)
plt.close()

print(f"[OK] Saved figure: {FIG_PATH}")
