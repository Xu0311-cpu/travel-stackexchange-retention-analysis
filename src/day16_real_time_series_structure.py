import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DAU_PATH = os.path.join(PROJECT_ROOT, "data", "day15_real_dau.csv")
D1_PATH = os.path.join(PROJECT_ROOT, "data", "day15_real_d1_retention.csv")
USER_DAY_PATH = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_user_day.csv")

OUT_MONTHLY = os.path.join(PROJECT_ROOT, "data", "day16_real_monthly_metrics.csv")
OUT_ROLLING = os.path.join(PROJECT_ROOT, "data", "day16_real_rolling_metrics.csv")

OUT_FIG_MONTHLY = os.path.join(PROJECT_ROOT, "figures", "day16_real_monthly_metrics.png")
OUT_FIG_ROLLING = os.path.join(PROJECT_ROOT, "figures", "day16_real_rolling_metrics.png")

OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day16.md")


# =========================
# Load
# =========================
def load_inputs():
    dau = pd.read_csv(DAU_PATH)
    d1 = pd.read_csv(D1_PATH)
    user_day = pd.read_csv(USER_DAY_PATH)

    dau["event_date"] = pd.to_datetime(dau["event_date"])
    d1["event_date"] = pd.to_datetime(d1["event_date"])
    user_day["event_date"] = pd.to_datetime(user_day["event_date"])

    return dau, d1, user_day


# =========================
# Monthly metrics
# =========================
def build_monthly_metrics(dau: pd.DataFrame, d1: pd.DataFrame, user_day: pd.DataFrame) -> pd.DataFrame:
    dau = dau.copy()
    d1 = d1.copy()
    user_day = user_day.copy()

    dau["month"] = dau["event_date"].dt.to_period("M").astype(str)
    d1["month"] = d1["event_date"].dt.to_period("M").astype(str)
    user_day["month"] = user_day["event_date"].dt.to_period("M").astype(str)

    monthly_dau = (
        dau.groupby("month")["dau"]
        .mean()
        .reset_index(name="avg_dau")
    )

    monthly_d1 = (
        d1.groupby("month")["d1_retention"]
        .mean()
        .reset_index(name="avg_d1_retention")
    )

    monthly_mau = (
        user_day.groupby("month")["user_id"]
        .nunique()
        .reset_index(name="mau")
    )

    monthly = (
        monthly_dau.merge(monthly_d1, on="month", how="outer")
        .merge(monthly_mau, on="month", how="outer")
        .sort_values("month")
        .reset_index(drop=True)
    )

    return monthly


# =========================
# Rolling metrics
# =========================
def build_rolling_metrics(dau: pd.DataFrame, d1: pd.DataFrame) -> pd.DataFrame:
    merged = dau.merge(d1, on="event_date", how="inner").sort_values("event_date").copy()

    merged["dau_90d_roll"] = merged["dau"].rolling(window=90, min_periods=30).mean()
    merged["d1_90d_roll"] = merged["d1_retention"].rolling(window=90, min_periods=30).mean()

    return merged


# =========================
# Plot
# =========================
def plot_monthly(monthly: pd.DataFrame, out_path: str):
    fig, ax1 = plt.subplots(figsize=(11, 5))

    x = pd.to_datetime(monthly["month"] + "-01")

    ax1.plot(x, monthly["avg_dau"], label="Avg DAU")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Avg DAU")

    ax2 = ax1.twinx()
    ax2.plot(x, monthly["mau"], linestyle="--", label="MAU")
    ax2.set_ylabel("MAU")

    ax1.set_title("Day16: Real Travel Monthly Activity Structure")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_rolling(rolling_df: pd.DataFrame, out_path: str):
    fig, ax1 = plt.subplots(figsize=(11, 5))

    x = rolling_df["event_date"]

    ax1.plot(x, rolling_df["dau_90d_roll"], label="DAU 90D Rolling Mean")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("DAU 90D Rolling Mean")

    ax2 = ax1.twinx()
    ax2.plot(x, rolling_df["d1_90d_roll"], linestyle="--", label="D1 90D Rolling Mean")
    ax2.set_ylabel("D1 90D Rolling Mean")

    ax1.set_title("Day16: Real Travel Rolling Activity & Retention")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Note
# =========================
def render_note(monthly: pd.DataFrame, rolling_df: pd.DataFrame) -> str:
    top_mau = monthly.sort_values("mau", ascending=False).head(10)
    top_avg_dau = monthly.sort_values("avg_dau", ascending=False).head(10)
    top_avg_d1 = monthly.sort_values("avg_d1_retention", ascending=False).head(10)

    first_month = monthly["month"].min()
    last_month = monthly["month"].max()

    peak_mau_row = monthly.loc[monthly["mau"].idxmax()]
    peak_dau_row = monthly.loc[monthly["avg_dau"].idxmax()]
    peak_d1_row = monthly.loc[monthly["avg_d1_retention"].idxmax()]

    latest_rolling = rolling_df.dropna(subset=["dau_90d_roll", "d1_90d_roll"]).iloc[-1]

    md = f"""# Day16

## 研究目标
Day15 已经计算了真实 Travel 社区的整体 DAU 与 D1 retention。  
但整体平均值会掩盖长期结构，因此 Day16 的目标是：

> 从时间序列角度识别 Travel 社区在 2011–2024 期间的活跃与留存结构变化。

---

## 今天完成的指标
### 月级指标
- `avg_dau`：月均 DAU
- `avg_d1_retention`：月均 D1 retention
- `mau`：月活跃用户数（月内去重）

### 滚动指标
- `dau_90d_roll`：90 天滚动平均 DAU
- `d1_90d_roll`：90 天滚动平均 D1 retention

---

## 数据覆盖范围
- 起始月份：**{first_month}**
- 结束月份：**{last_month}**

---

## 月级峰值
- 峰值 MAU：**{int(peak_mau_row['mau'])}**（月份：**{peak_mau_row['month']}**）
- 峰值月均 DAU：**{peak_dau_row['avg_dau']:.2f}**（月份：**{peak_dau_row['month']}**）
- 峰值月均 D1 retention：**{peak_d1_row['avg_d1_retention']:.4f}**（月份：**{peak_d1_row['month']}**）

---

## 最新滚动水平
- 最新 90 天滚动平均 DAU：**{latest_rolling['dau_90d_roll']:.2f}**
- 最新 90 天滚动平均 D1 retention：**{latest_rolling['d1_90d_roll']:.4f}**

---

## MAU Top 10 月份
{top_mau.to_markdown(index=False)}

---

## 月均 DAU Top 10 月份
{top_avg_dau.to_markdown(index=False)}

---

## 月均 D1 retention Top 10 月份
{top_avg_d1.to_markdown(index=False)}

---

## 今日核心观察
1. 真实社区指标不能只看整体均值，必须放回时间轴上看阶段变化。
2. MAU、月均 DAU 与月均 D1 retention 不一定同步变化，这有助于区分“规模变化”和“粘性变化”。
3. 滚动平均让我们可以看到长期趋势，而不是被日级波动误导。

---

## 方法边界
- 当前仍是整体站点层级分析，还没有拆用户类型和行为类型。
- 月均 D1 retention 只是时间压缩后的整体指标，后续仍需结合动作分层或 cohort 分析。
- 90 天窗口是经验性设定，不是唯一正确窗口。

---

## 下一步
Day17 可以优先进入两条线中的一条：
1. **动作分层线**：比较 question / answer / comment 用户的次日留存差异
2. **阶段结构线**：按年份或阶段（早期/成熟期）比较社区行为模式变化
"""
    return md


# =========================
# Main
# =========================
def main():
    dau, d1, user_day = load_inputs()

    monthly = build_monthly_metrics(dau, d1, user_day)
    rolling_df = build_rolling_metrics(dau, d1)

    monthly.to_csv(OUT_MONTHLY, index=False)
    rolling_df.to_csv(OUT_ROLLING, index=False)

    plot_monthly(monthly, OUT_FIG_MONTHLY)
    plot_rolling(rolling_df, OUT_FIG_ROLLING)

    note = render_note(monthly, rolling_df)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved monthly metrics:", OUT_MONTHLY)
    print("[OK] Saved rolling metrics:", OUT_ROLLING)
    print("[OK] Saved monthly figure:", OUT_FIG_MONTHLY)
    print("[OK] Saved rolling figure:", OUT_FIG_ROLLING)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Monthly Summary ===")
    print(monthly[["avg_dau", "avg_d1_retention", "mau"]].describe().to_string())

    print("\n=== Peak Months ===")
    print("Peak MAU month:")
    print(monthly.loc[monthly["mau"].idxmax()].to_string())
    print("\nPeak avg DAU month:")
    print(monthly.loc[monthly["avg_dau"].idxmax()].to_string())
    print("\nPeak avg D1 month:")
    print(monthly.loc[monthly["avg_d1_retention"].idxmax()].to_string())


if __name__ == "__main__":
    main()