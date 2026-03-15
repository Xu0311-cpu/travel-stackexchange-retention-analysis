import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_DAY_PATH = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_user_day.csv")

OUT_DAU = os.path.join(PROJECT_ROOT, "data", "day15_real_dau.csv")
OUT_D1 = os.path.join(PROJECT_ROOT, "data", "day15_real_d1_retention.csv")

OUT_DAU_FIG = os.path.join(PROJECT_ROOT, "figures", "day15_real_dau.png")
OUT_D1_FIG = os.path.join(PROJECT_ROOT, "figures", "day15_real_d1_retention.png")

OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day15.md")


# =========================
# Step 1: Load
# =========================
def load_user_day() -> pd.DataFrame:
    df = pd.read_csv(USER_DAY_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
    return df


# =========================
# Step 2: DAU
# =========================
def build_dau(df: pd.DataFrame) -> pd.DataFrame:
    dau = (
        df.groupby("event_date")["user_id"]
        .nunique()
        .reset_index(name="dau")
        .sort_values("event_date")
    )
    return dau


# =========================
# Step 3: D1 retention
# =========================
def build_d1_retention(df: pd.DataFrame) -> pd.DataFrame:
    """
    定义：
    - base day: 某天活跃的用户集合
    - retained: 次日仍活跃的用户集合
    """
    tmp = df[["user_id", "event_date"]].drop_duplicates().copy()

    # 为每个 user-day 构造 next_day
    tmp["next_day"] = pd.to_datetime(tmp["event_date"]) + pd.Timedelta(days=1)
    tmp["next_day"] = tmp["next_day"].dt.date

    # 右表只保留“真实活跃日期”，避免 next_day 列重名
    next_active = (
        tmp[["user_id", "event_date"]]
        .drop_duplicates()
        .rename(columns={"event_date": "active_date"})
        .copy()
    )

    merged = tmp.merge(
        next_active,
        left_on=["user_id", "next_day"],
        right_on=["user_id", "active_date"],
        how="left"
    )

    merged["retained_next_day"] = merged["active_date"].notna().astype(int)

    d1 = (
        merged.groupby("event_date")
        .agg(
            base_users=("user_id", "nunique"),
            retained_users=("retained_next_day", "sum")
        )
        .reset_index()
        .sort_values("event_date")
    )

    d1["d1_retention"] = d1["retained_users"] / d1["base_users"]

    return d1


# =========================
# Step 4: Plot
# =========================
def plot_dau(dau: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(pd.to_datetime(dau["event_date"]), dau["dau"])
    ax.set_title("Day15: Real Travel DAU")
    ax.set_xlabel("Date")
    ax.set_ylabel("DAU")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_d1(d1: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(pd.to_datetime(d1["event_date"]), d1["d1_retention"])
    ax.set_title("Day15: Real Travel D1 Retention")
    ax.set_xlabel("Date")
    ax.set_ylabel("D1 retention")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 5: Note
# =========================
def render_note(dau: pd.DataFrame, d1: pd.DataFrame) -> str:
    avg_dau = dau["dau"].mean()
    median_dau = dau["dau"].median()
    max_dau_row = dau.loc[dau["dau"].idxmax()]

    avg_d1 = d1["d1_retention"].mean()
    median_d1 = d1["d1_retention"].median()
    max_d1_row = d1.loc[d1["d1_retention"].idxmax()]
    min_d1_row = d1.loc[d1["d1_retention"].idxmin()]

    top_dau_days = dau.sort_values("dau", ascending=False).head(10)
    top_d1_days = d1.sort_values("d1_retention", ascending=False).head(10)

    md = f"""# Day15

## 研究目标
Day15 把之前在 toy 数据上完成的 Day1 / Day2 核心指标分析，正式迁移到真实 Travel Stack Exchange 数据上。

本日完成两个核心指标：

1. **DAU（Daily Active Users）**
2. **D1 retention**

---

## 指标定义

### DAU
某一天至少发生过一次行为的独立用户数。

### D1 retention
某一天活跃过的用户中，第二天仍然活跃的比例。

公式：

D1 retention = retained_users / base_users

其中：
- `base_users` = 当天活跃用户数
- `retained_users` = 次日仍活跃的用户数

---

## DAU 结果概览
- 平均 DAU：**{avg_dau:.2f}**
- 中位数 DAU：**{median_dau:.2f}**
- 最大 DAU：**{int(max_dau_row['dau'])}**（日期：**{max_dau_row['event_date']}**）

### DAU 最高的 Top 10 日期
{top_dau_days.to_markdown(index=False)}

---

## D1 retention 结果概览
- 平均 D1 retention：**{avg_d1:.4f}**
- 中位数 D1 retention：**{median_d1:.4f}**
- 最高 D1 retention：**{max_d1_row['d1_retention']:.4f}**（日期：**{max_d1_row['event_date']}**）
- 最低 D1 retention：**{min_d1_row['d1_retention']:.4f}**（日期：**{min_d1_row['event_date']}**）

### D1 retention 最高的 Top 10 日期
{top_d1_days[['event_date', 'base_users', 'retained_users', 'd1_retention']].to_markdown(index=False)}

---

## 今日核心观察
1. 真实 Travel 数据已经能够稳定计算 DAU 和 D1 retention，说明 Day14 构造的 user-day 表是有效的分析底表。
2. 真实社区的 DAU 与留存会受到长期时间跨度影响，因此后续不能只看整体平均值，还需要结合时间序列观察结构变化。
3. 到 Day15 为止，toy 项目里的核心指标层已经成功迁移到了真实项目。

---

## 方法边界
- 当前 D1 retention 是站点层级的整体 retention，不区分用户类型或行为类型。
- 整体平均值可能会掩盖长期趋势变化，因此后续需要进入时间序列和分层分析。
- 由于真实数据没有 view 日志，所以后续行为分析需要围绕 `question / answer / comment` 重新定义状态和参与层级。

---

## 下一步
Day16 可以继续：
1. 画出更清晰的时间序列结构（例如按年或月聚合）
2. 拆分不同动作类型对留存的关系
3. 开始重新定义真实数据里的“浅参与 / 深参与”状态
"""
    return md


# =========================
# Main
# =========================
def main():
    df = load_user_day()

    dau = build_dau(df)
    d1 = build_d1_retention(df)

    dau.to_csv(OUT_DAU, index=False)
    d1.to_csv(OUT_D1, index=False)

    plot_dau(dau, OUT_DAU_FIG)
    plot_d1(d1, OUT_D1_FIG)

    note = render_note(dau, d1)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved DAU:", OUT_DAU)
    print("[OK] Saved D1 retention:", OUT_D1)
    print("[OK] Saved DAU figure:", OUT_DAU_FIG)
    print("[OK] Saved D1 figure:", OUT_D1_FIG)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== DAU Summary ===")
    print(dau.describe(include="all").to_string())

    print("\n=== D1 Summary ===")
    print(d1[["base_users", "retained_users", "d1_retention"]].describe().to_string())


if __name__ == "__main__":
    main()