import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_DAY_PATH = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_user_day.csv")

OUT_STAGE_RETENTION = os.path.join(PROJECT_ROOT, "data", "day19_real_action_retention_by_stage.csv")
OUT_STAGE_STATS = os.path.join(PROJECT_ROOT, "data", "day19_real_action_stage_stats.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day19_real_action_retention_by_stage.png")
OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day19.md")


# =========================
# Load
# =========================
def load_user_day() -> pd.DataFrame:
    df = pd.read_csv(USER_DAY_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"])
    return df


# =========================
# Step 1: Add action segment
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
# Step 2: Add stage
# =========================
def add_stage(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    year = df["event_date"].dt.year

    conditions = [
        year.between(2011, 2014),
        year.between(2015, 2019),
        year.between(2020, 2024),
    ]
    choices = ["early_stage", "middle_stage", "late_stage"]

    df["stage"] = pd.Series(index=df.index, dtype="object")
    df.loc[conditions[0], "stage"] = choices[0]
    df.loc[conditions[1], "stage"] = choices[1]
    df.loc[conditions[2], "stage"] = choices[2]

    return df


# =========================
# Step 3: Add next-day retained label
# =========================
def add_next_day_active(df: pd.DataFrame) -> pd.DataFrame:
    base = df[["user_id", "event_date", "action_segment", "stage"]].drop_duplicates().copy()

    base["next_day"] = base["event_date"] + pd.Timedelta(days=1)

    active_next = (
        df[["user_id", "event_date"]]
        .drop_duplicates()
        .rename(columns={"event_date": "active_date"})
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
# Step 4: Aggregate by stage
# =========================
def build_stage_tables(merged: pd.DataFrame):
    focus = ["comment_only_user_day", "question_user_day", "answer_user_day"]
    tmp = merged[merged["action_segment"].isin(focus)].copy()

    stage_ret = (
        tmp.groupby(["stage", "action_segment"])
        .agg(
            base_users=("user_id", "count"),
            retained_users=("retained_next_day", "sum")
        )
        .reset_index()
    )
    stage_ret["d1_retention"] = stage_ret["retained_users"] / stage_ret["base_users"]

    stage_stats = (
        stage_ret.groupby("action_segment")
        .agg(
            mean_retention=("d1_retention", "mean"),
            min_retention=("d1_retention", "min"),
            max_retention=("d1_retention", "max")
        )
        .reset_index()
        .sort_values("mean_retention", ascending=False)
    )

    return stage_ret, stage_stats


# =========================
# Step 5: Plot
# =========================
def plot_stage_retention(stage_ret: pd.DataFrame, out_path: str):
    order_stage = ["early_stage", "middle_stage", "late_stage"]
    order_action = ["comment_only_user_day", "question_user_day", "answer_user_day"]

    pivot = (
        stage_ret.pivot(index="stage", columns="action_segment", values="d1_retention")
        .loc[order_stage, order_action]
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    pivot.plot(kind="bar", ax=ax)

    ax.set_title("Day19: D1 Retention by Action Segment and Community Stage")
    ax.set_xlabel("Stage")
    ax.set_ylabel("D1 retention")
    ax.legend(title="Action segment")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 6: Note
# =========================
def render_note(stage_ret: pd.DataFrame, stage_stats: pd.DataFrame) -> str:
    order_stage = ["early_stage", "middle_stage", "late_stage"]
    order_action = ["comment_only_user_day", "question_user_day", "answer_user_day"]

    stage_ret = stage_ret.copy()
    stage_ret["stage"] = pd.Categorical(stage_ret["stage"], categories=order_stage, ordered=True)
    stage_ret["action_segment"] = pd.Categorical(stage_ret["action_segment"], categories=order_action, ordered=True)
    stage_ret = stage_ret.sort_values(["stage", "action_segment"])

    answer_rows = stage_ret[stage_ret["action_segment"] == "answer_user_day"].copy()
    comment_rows = stage_ret[stage_ret["action_segment"] == "comment_only_user_day"].copy()
    question_rows = stage_ret[stage_ret["action_segment"] == "question_user_day"].copy()

    md = f"""# Day19

## 研究目标
Day19 进一步检验：  
> **不同动作类型的留存差异，是否在社区不同发展阶段中仍然成立？**

为此，将 Travel 社区划分为三个阶段：
- `early_stage`：2011–2014
- `middle_stage`：2015–2019
- `late_stage`：2020–2024

---

## 分阶段动作留存结果
{stage_ret.to_markdown(index=False)}

---

## 跨阶段汇总
{stage_stats.to_markdown(index=False)}

---

## 今日核心观察
1. `answer_user_day` 在不同阶段中的留存水平分别为：
{answer_rows[['stage', 'd1_retention']].to_markdown(index=False)}

2. `comment_only_user_day` 在不同阶段中的留存水平分别为：
{comment_rows[['stage', 'd1_retention']].to_markdown(index=False)}

3. `question_user_day` 在不同阶段中的留存水平分别为：
{question_rows[['stage', 'd1_retention']].to_markdown(index=False)}

---

## 业务解释
如果回答型行为在早期、中期、后期都保持相对更高留存，那么可以更有信心地说：

> **高价值内容供给行为并不是某个单一时期的偶然现象，而是社区生态中更稳定的高质量参与信号。**

这会让项目从“单点发现”升级成“跨阶段稳定洞察”。

---

## 方法边界
- 阶段划分是人为设定的，目的是形成业务可解释的结构比较
- 这仍然是观察性分析，不代表 answer 行为对留存具有因果作用
- 后续仍可以进一步做更细阶段切分或用户层控制

---

## 下一步
Day20 建议进入最终包装阶段：
1. README 首页
2. 简历 bullets
3. 2 分钟项目讲稿
4. 推荐展示图清单
"""
    return md


# =========================
# Main
# =========================
def main():
    df = load_user_day()
    df = add_action_segment(df)
    df = add_stage(df)
    merged = add_next_day_active(df)

    stage_ret, stage_stats = build_stage_tables(merged)

    stage_ret.to_csv(OUT_STAGE_RETENTION, index=False)
    stage_stats.to_csv(OUT_STAGE_STATS, index=False)

    plot_stage_retention(stage_ret, OUT_FIG)

    note = render_note(stage_ret, stage_stats)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved stage retention:", OUT_STAGE_RETENTION)
    print("[OK] Saved stage stats:", OUT_STAGE_STATS)
    print("[OK] Saved figure:", OUT_FIG)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Retention by Stage ===")
    print(stage_ret.to_string(index=False))

    print("\n=== Cross-stage Summary ===")
    print(stage_stats.to_string(index=False))


if __name__ == "__main__":
    main()