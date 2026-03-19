import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_DAY_PATH = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_user_day.csv")

OUT_RETENTION = os.path.join(PROJECT_ROOT, "data", "day17_real_retention_by_action.csv")
OUT_DAILY = os.path.join(PROJECT_ROOT, "data", "day17_real_daily_retention_by_action.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day17_real_retention_by_action.png")
OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day17.md")


# =========================
# Load
# =========================
def load_user_day() -> pd.DataFrame:
    df = pd.read_csv(USER_DAY_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
    return df


# =========================
# Step 1: Define action segment
# =========================
def add_action_segment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def classify(row):
        if row["answer_cnt"] > 0:
            return "answer_user_day"
        elif row["question_cnt"] > 0:
            return "question_user_day"
        elif row["comment_cnt"] > 0 and row["question_cnt"] == 0 and row["answer_cnt"] == 0:
            return "comment_only_user_day"
        else:
            return "other"

    df["action_segment"] = df.apply(classify, axis=1)
    return df


# =========================
# Step 2: Add next-day active label
# =========================
def add_next_day_active(df: pd.DataFrame) -> pd.DataFrame:
    base = df[["user_id", "event_date", "action_segment"]].drop_duplicates().copy()

    base["next_day"] = pd.to_datetime(base["event_date"]) + pd.Timedelta(days=1)
    base["next_day"] = base["next_day"].dt.date

    active_next = (
        df[["user_id", "event_date"]]
        .drop_duplicates()
        .rename(columns={"event_date": "active_date"})
        .copy()
    )

    merged = base.merge(
        active_next,
        left_on=["user_id", "next_day"],
        right_on=["user_id", "active_date"],
        how="left"
    )

    merged["retained_next_day"] = merged["active_date"].notna().astype(int)
    return merged


# =========================
# Step 3: Aggregate retention
# =========================
def build_retention_tables(merged: pd.DataFrame):
    focus_segments = ["comment_only_user_day", "question_user_day", "answer_user_day"]
    tmp = merged[merged["action_segment"].isin(focus_segments)].copy()

    overall = (
        tmp.groupby("action_segment")
        .agg(
            base_users=("user_id", "count"),
            retained_users=("retained_next_day", "sum")
        )
        .reset_index()
    )
    overall["d1_retention"] = overall["retained_users"] / overall["base_users"]

    daily = (
        tmp.groupby(["event_date", "action_segment"])
        .agg(
            base_users=("user_id", "count"),
            retained_users=("retained_next_day", "sum")
        )
        .reset_index()
    )
    daily["d1_retention"] = daily["retained_users"] / daily["base_users"]

    return overall.sort_values("d1_retention", ascending=False), daily


# =========================
# Step 4: Plot
# =========================
def plot_retention(overall: pd.DataFrame, out_path: str):
    plot_df = overall.set_index("action_segment").loc[
        ["comment_only_user_day", "question_user_day", "answer_user_day"]
    ]

    fig, ax = plt.subplots(figsize=(7, 4))
    plot_df["d1_retention"].plot(kind="bar", ax=ax)

    ax.set_title("Day17: Real Travel D1 Retention by Action Segment")
    ax.set_ylabel("D1 retention")
    ax.set_xlabel("Action segment")

    for i, v in enumerate(plot_df["d1_retention"].values):
        ax.text(i, v + 0.01, f"{v:.3f}", ha="center")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 5: Note
# =========================
def render_note(overall: pd.DataFrame, daily: pd.DataFrame) -> str:
    focus_order = ["comment_only_user_day", "question_user_day", "answer_user_day"]
    overall = overall.set_index("action_segment").loc[focus_order].reset_index()

    best = overall.sort_values("d1_retention", ascending=False).iloc[0]
    worst = overall.sort_values("d1_retention", ascending=True).iloc[0]

    daily_stats = (
        daily.groupby("action_segment")["d1_retention"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    md = f"""# Day17

## 研究目标
Day17 把 toy 项目里的“按 action 看留存”正式迁移到真实 Travel 数据。

核心问题是：

> 在真实社区里，不同类型的参与行为，是否与不同水平的次日留存相关？

---

## 行为分层定义
为了让真实数据更接近业务解释，本日将 user-day 分成三类：

- **comment_only_user_day**：当天只有 comment，没有 question / answer
- **question_user_day**：当天至少有 1 次 question
- **answer_user_day**：当天至少有 1 次 answer

这个分层可以近似理解为：
- `comment_only` = 较浅互动
- `question` = 主动发起参与
- `answer` = 更深的内容贡献

---

## 总体结果
{overall.to_markdown(index=False)}

---

## 按日分布统计
{daily_stats.to_markdown(index=False)}

---

## 今日核心观察
- 留存最高的动作分层：**{best['action_segment']}**，D1 retention = **{best['d1_retention']:.4f}**
- 留存最低的动作分层：**{worst['action_segment']}**，D1 retention = **{worst['d1_retention']:.4f}**

这说明在真实社区中，不同参与深度对应的短期回访水平并不相同。  
相比只看 overall retention，这一步更接近“行为机制分析”。

---

## 商业化解释
如果把 Travel Stack Exchange 视为一个知识社区产品，那么：

- `comment_only` 可以理解为轻互动用户
- `question` 可以理解为主动表达需求的用户
- `answer` 可以理解为贡献高价值内容的用户

因此，这一步实际上是在回答一个更接近业务的问题：

> **哪类参与行为，更有可能与次日回访和持续活跃相关？**

这个问题在社区运营、内容平台、用户增长分析里都非常常见。

---

## 方法边界
- 当前仍然是观察性分析，只能说明“行为分层与留存相关”，不能解释因果
- `answer_user_day` 和 `question_user_day` 可能存在用户能力差异、自选择偏差
- 后续仍需结合 base size、时间阶段和更严格的稳健性分析

---

## 下一步
Day18 可以继续两条线：
1. **稳健性线**：给 action retention 加上 CI / base size / 时间分段对比
2. **简历包装线**：把整个真实项目整理成“社区增长 / 用户留存分析案例”
"""
    return md


# =========================
# Main
# =========================
def main():
    df = load_user_day()
    df = add_action_segment(df)

    merged = add_next_day_active(df)
    overall, daily = build_retention_tables(merged)

    overall.to_csv(OUT_RETENTION, index=False)
    daily.to_csv(OUT_DAILY, index=False)

    plot_retention(overall, OUT_FIG)

    note = render_note(overall, daily)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved overall retention:", OUT_RETENTION)
    print("[OK] Saved daily retention:", OUT_DAILY)
    print("[OK] Saved figure:", OUT_FIG)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Overall Retention by Action ===")
    print(overall.to_string(index=False))

    print("\n=== Daily Retention Stats ===")
    print(
        daily.groupby("action_segment")["d1_retention"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .sort_values("mean", ascending=False)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()