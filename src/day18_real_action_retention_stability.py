import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_DAY_PATH = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_user_day.csv")

OUT_OVERALL = os.path.join(PROJECT_ROOT, "data", "day18_real_action_retention_stability.csv")
OUT_DAILY = os.path.join(PROJECT_ROOT, "data", "day18_real_action_daily_retention.csv")
OUT_CI = os.path.join(PROJECT_ROOT, "data", "day18_real_action_retention_ci.csv")

OUT_FIG_RET = os.path.join(PROJECT_ROOT, "figures", "day18_real_action_retention_with_ci.png")
OUT_FIG_VOL = os.path.join(PROJECT_ROOT, "figures", "day18_real_action_daily_volatility.png")

OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day18.md")

BOOTSTRAP_B = 1000
RANDOM_SEED = 42


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
# Step 2: Add next-day retained label
# =========================
def add_next_day_active(df: pd.DataFrame) -> pd.DataFrame:
    base = df[["user_id", "event_date", "action_segment"]].drop_duplicates().copy()

    base["next_day"] = pd.to_datetime(base["event_date"]) + pd.Timedelta(days=1)
    base["next_day"] = base["next_day"].dt.date

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
# Step 3: Aggregate
# =========================
def build_tables(merged: pd.DataFrame):
    focus = ["comment_only_user_day", "question_user_day", "answer_user_day"]
    tmp = merged[merged["action_segment"].isin(focus)].copy()

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

    return overall, daily


# =========================
# Step 4: Bootstrap CI by user-day rows
# =========================
def bootstrap_ci(tmp: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    focus = ["comment_only_user_day", "question_user_day", "answer_user_day"]

    point = (
        tmp.groupby("action_segment")
        .agg(
            base_users=("user_id", "count"),
            retained_users=("retained_next_day", "sum")
        )
        .reset_index()
    )
    point["d1_retention"] = point["retained_users"] / point["base_users"]

    boot_records = []

    for seg in focus:
        seg_df = tmp[tmp["action_segment"] == seg].copy()

        if len(seg_df) == 0:
            continue

        rates = []
        for _ in range(BOOTSTRAP_B):
            sample = seg_df.sample(n=len(seg_df), replace=True, random_state=rng.integers(1e9))
            rate = sample["retained_next_day"].mean()
            rates.append(rate)

        ci_low = np.quantile(rates, 0.025)
        ci_high = np.quantile(rates, 0.975)

        boot_records.append([seg, ci_low, ci_high])

    ci_df = pd.DataFrame(boot_records, columns=["action_segment", "ci_low", "ci_high"])
    out = point.merge(ci_df, on="action_segment", how="left")
    return out


# =========================
# Step 5: Plot
# =========================
def plot_retention_with_ci(ci_df: pd.DataFrame, out_path: str):
    order = ["comment_only_user_day", "question_user_day", "answer_user_day"]
    plot_df = ci_df.set_index("action_segment").loc[order].reset_index()

    x = np.arange(len(plot_df))
    y = plot_df["d1_retention"].values
    yerr = np.vstack([
        y - plot_df["ci_low"].values,
        plot_df["ci_high"].values - y
    ])

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x, y)
    ax.errorbar(x, y, yerr=yerr, fmt="none", capsize=5)

    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["action_segment"])
    ax.set_ylabel("D1 retention")
    ax.set_title("Day18: Real Action-level D1 Retention with 95% CI")

    for i, v in enumerate(y):
        ax.text(i, v + 0.01, f"{v:.3f}", ha="center")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_daily_volatility(daily: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 5))

    for seg, seg_df in daily.groupby("action_segment"):
        seg_df = seg_df.sort_values("event_date")
        ax.plot(pd.to_datetime(seg_df["event_date"]), seg_df["d1_retention"], label=seg, alpha=0.7)

    ax.set_title("Day18: Daily D1 Retention Volatility by Action Segment")
    ax.set_xlabel("Date")
    ax.set_ylabel("D1 retention")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 6: Note
# =========================
def render_note(ci_df: pd.DataFrame, daily: pd.DataFrame) -> str:
    order = ["comment_only_user_day", "question_user_day", "answer_user_day"]
    ci_df = ci_df.set_index("action_segment").loc[order].reset_index()

    daily_stats = (
        daily.groupby("action_segment")
        .agg(
            mean_retention=("d1_retention", "mean"),
            std_retention=("d1_retention", "std"),
            mean_base=("base_users", "mean"),
            median_base=("base_users", "median"),
            observed_days=("event_date", "count")
        )
        .reset_index()
        .sort_values("mean_retention", ascending=False)
    )

    best = ci_df.sort_values("d1_retention", ascending=False).iloc[0]

    md = f"""# Day18

## 研究目标
Day17 已经发现不同动作分层的 D1 retention 存在明显差异。  
Day18 的目标是进一步判断：

> 这些差异是否具有基本稳定性，而不是由样本量过小或日级波动偶然造成？

---

## 今天补充的稳定性信息
1. **总体 base size**
2. **总体 D1 retention**
3. **95% bootstrap CI**
4. **日级 retention 波动统计**

---

## Overall retention with CI
{ci_df.to_markdown(index=False)}

---

## Daily volatility stats
{daily_stats.to_markdown(index=False)}

---

## 今日核心观察
- 留存最高的动作分层仍然是：**{best['action_segment']}**
- 其 D1 retention = **{best['d1_retention']:.4f}**
- 95% CI = **[{best['ci_low']:.4f}, {best['ci_high']:.4f}]**

这说明 Day17 观察到的“回答型行为与更高短期留存相关”并不只是一个裸点估计，而是在较大 base 和不确定性范围下仍保持优势。

---

## 商业化解释
如果把这个知识社区看成一个产品生态，那么：
- `question` 更像需求表达
- `comment_only` 更像轻互动
- `answer` 更像高价值供给

Day18 的意义在于把结论从“发现差异”推进到“验证差异是否有基本稳定性”，这比单纯给出一个 retention 数字更接近真实业务分析。

---

## 方法边界
- 这里的 CI 仍然基于观察性数据，不代表因果效应
- `answer_user_day` 可能天然聚集更资深、更高意愿用户
- 后续如果要继续提升严谨性，可以做时间分段比较或用户层分层控制

---

## 下一步
Day19 建议进入：
1. **阶段分段比较**：早期 vs 成熟期，动作留存是否变化
2. **项目包装**：整理成 README + 简历 bullet + 面试讲法
"""
    return md


# =========================
# Main
# =========================
def main():
    df = load_user_day()
    df = add_action_segment(df)
    merged = add_next_day_active(df)

    overall, daily = build_tables(merged)
    focus = merged[merged["action_segment"].isin(["comment_only_user_day", "question_user_day", "answer_user_day"])].copy()
    ci_df = bootstrap_ci(focus)

    overall.to_csv(OUT_OVERALL, index=False)
    daily.to_csv(OUT_DAILY, index=False)
    ci_df.to_csv(OUT_CI, index=False)

    plot_retention_with_ci(ci_df, OUT_FIG_RET)
    plot_daily_volatility(daily, OUT_FIG_VOL)

    note = render_note(ci_df, daily)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved overall stability table:", OUT_OVERALL)
    print("[OK] Saved daily retention table:", OUT_DAILY)
    print("[OK] Saved CI table:", OUT_CI)
    print("[OK] Saved retention+CI figure:", OUT_FIG_RET)
    print("[OK] Saved volatility figure:", OUT_FIG_VOL)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Retention with CI ===")
    print(ci_df.to_string(index=False))

    print("\n=== Daily Volatility Stats ===")
    print(
        daily.groupby("action_segment")
        .agg(
            mean_retention=("d1_retention", "mean"),
            std_retention=("d1_retention", "std"),
            mean_base=("base_users", "mean"),
            median_base=("base_users", "median"),
            observed_days=("event_date", "count")
        )
        .reset_index()
        .sort_values("mean_retention", ascending=False)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()