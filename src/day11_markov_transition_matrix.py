import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_STATE_DETAIL = os.path.join(PROJECT_ROOT, "data", "day11_state_detail.csv")
OUT_TRANSITION = os.path.join(PROJECT_ROOT, "data", "day11_transition_matrix.csv")
OUT_TRANSITION_CI = os.path.join(PROJECT_ROOT, "data", "day11_transition_matrix_ci.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day11_transition_matrix.png")
OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day11.md")

TRAVEL = "travel"
BOOTSTRAP_B = 1000
RANDOM_SEED = 42
CI_ALPHA = 0.05

STATE_ORDER = ["inactive", "view_only", "engaged"]


# =========================
# Step 1: Build daily state
# =========================
def classify_state(day_user_df: pd.DataFrame) -> str:
    """
    输入：某用户某天在 travel 的所有行为
    输出：状态
    """
    if len(day_user_df) == 0:
        return "inactive"

    n_events = len(day_user_df)
    actions = set(day_user_df["action"].tolist())

    # 只有1个行为，且是view
    if n_events == 1 and actions == {"view"}:
        return "view_only"

    # 其他有行为的情况都归为 engaged
    return "engaged"


def build_state_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    构建 user-date 状态面板：
    对所有用户、所有日期补全，再给每个 user-day 分配一个状态
    """
    df = df.copy()
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    df_t = df[df["community"] == TRAVEL].copy()

    all_users = sorted(df_t["user_id"].unique())
    all_dates = pd.date_range(df_t["event_date"].min(), df_t["event_date"].max(), freq="D").date

    # 原始 user-day 行为
    grouped = {
        (d, u): g.copy()
        for (d, u), g in df_t.groupby(["event_date", "user_id"])
    }

    rows = []
    for d in all_dates:
        for u in all_users:
            day_user_df = grouped.get((d, u), pd.DataFrame(columns=df_t.columns))
            state = classify_state(day_user_df)
            rows.append([d, u, state])

    panel = pd.DataFrame(rows, columns=["date", "user_id", "state"])
    return panel


# =========================
# Step 2: Build transitions
# =========================
def build_transitions(panel: pd.DataFrame) -> pd.DataFrame:
    """
    构建 t -> t+1 的状态转移
    """
    panel = panel.sort_values(["user_id", "date"]).copy()
    panel["next_state"] = panel.groupby("user_id")["state"].shift(-1)
    trans = panel.dropna(subset=["next_state"]).copy()
    return trans


def transition_matrix(trans: pd.DataFrame) -> pd.DataFrame:
    """
    计算转移概率矩阵
    """
    cnt = (
        trans.groupby(["state", "next_state"])
        .size()
        .reset_index(name="n")
    )

    all_pairs = pd.MultiIndex.from_product(
        [STATE_ORDER, STATE_ORDER],
        names=["state", "next_state"]
    ).to_frame(index=False)

    cnt = all_pairs.merge(cnt, on=["state", "next_state"], how="left").fillna(0)

    row_sum = cnt.groupby("state")["n"].transform("sum")
    cnt["prob"] = np.where(row_sum > 0, cnt["n"] / row_sum, np.nan)

    mat = cnt.pivot(index="state", columns="next_state", values="prob").loc[STATE_ORDER, STATE_ORDER]
    return mat


# =========================
# Step 3: Bootstrap CI
# =========================
def bootstrap_transition_ci(trans: pd.DataFrame) -> pd.DataFrame:
    """
    按 user_id 做 cluster bootstrap
    """
    rng = np.random.default_rng(RANDOM_SEED)
    users = trans["user_id"].unique()

    by_user = {u: trans[trans["user_id"] == u] for u in users}

    records = []

    for _ in range(BOOTSTRAP_B):
        sampled_users = rng.choice(users, size=len(users), replace=True)
        boot_df = pd.concat([by_user[u] for u in sampled_users], ignore_index=True)

        mat = transition_matrix(boot_df)

        for s in STATE_ORDER:
            for ns in STATE_ORDER:
                records.append([s, ns, mat.loc[s, ns]])

    boot = pd.DataFrame(records, columns=["state", "next_state", "prob"])

    lo_q = CI_ALPHA / 2
    hi_q = 1 - CI_ALPHA / 2

    ci = (
        boot.groupby(["state", "next_state"])["prob"]
        .quantile([lo_q, hi_q])
        .unstack()
        .reset_index()
    )
    ci.columns = ["state", "next_state", "ci_low", "ci_high"]

    point = transition_matrix(trans).stack().reset_index()
    point.columns = ["state", "next_state", "prob"]

    out = point.merge(ci, on=["state", "next_state"], how="left")
    return out


# =========================
# Step 4: Plot
# =========================
def plot_transition_matrix(mat: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(mat.values)

    ax.set_xticks(range(len(mat.columns)))
    ax.set_xticklabels(mat.columns)
    ax.set_yticks(range(len(mat.index)))
    ax.set_yticklabels(mat.index)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{mat.iloc[i, j]:.2f}", ha="center", va="center")

    ax.set_title("Day11: State Transition Matrix (travel)")
    fig.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 5: Note
# =========================
def render_note(mat: pd.DataFrame, ci_df: pd.DataFrame) -> str:
    long_df = mat.stack().reset_index()
    long_df.columns = ["state", "next_state", "prob"]
    long_df = long_df.sort_values(["state", "prob"], ascending=[True, False])

    lines = []
    for s in STATE_ORDER:
        tmp = long_df[long_df["state"] == s].sort_values("prob", ascending=False)
        top = tmp.iloc[0]
        lines.append(
            f"- 从 **{s}** 出发，次日最可能转移到 **{top['next_state']}**，概率约为 **{top['prob']:.2f}**。"
        )

    md = f"""# Day11

## 研究问题
在 travel 社区中，用户不是静止地停留在某个参与层级，而是在不同状态之间流动。  
因此，Day11 的问题是：**用户今天所处的状态，会如何影响他明天最可能进入的状态？**

## 状态定义
- **inactive**：当天在 travel 没有行为
- **view_only**：当天在 travel 只有 1 个行为，且该行为是 `view`
- **engaged**：当天在 travel 有更深参与（例如 `comment / like / post`），或当天有 2 个及以上行为

## 方法
1. 先对每个 user-day 定义状态  
2. 再构造 `today_state -> next_day_state` 的转移对  
3. 计算转移概率矩阵  
4. 用 cluster bootstrap（按 user）估计转移概率的不确定性

## 转移矩阵
{mat.to_markdown()}

## 核心观察
{chr(10).join(lines)}

## 方法上的意义
这一步把前面的静态留存/分层分析，推进成了**动态行为路径分析**。  
相比只看 retention，高阶一点的价值在于：
- 可以看到“用户是怎么流动的”
- 可以识别哪些状态最容易掉回 inactive
- 可以观察哪些状态更有机会升级到更高参与

## 结论边界
- 这仍然是观察性分析，只能描述行为迁移结构，不能解释因果
- 状态定义是人为简化的，不同分法可能会影响矩阵结果
- toy 数据规模有限，因此矩阵适合用来练分析链条，不适合做强业务结论

## 下一步
Day12 可以沿两条线推进：
1. 在状态迁移基础上做更细的路径分析（例如 view_only → engaged 的重点比较）
2. 开始做最简逻辑回归，用状态和近期行为预测次日留存
"""
    return md


# =========================
# Main
# =========================
def main():
    df = pd.read_csv(DATA_PATH)

    panel = build_state_panel(df)
    panel.to_csv(OUT_STATE_DETAIL, index=False)

    trans = build_transitions(panel)

    mat = transition_matrix(trans)
    mat.to_csv(OUT_TRANSITION)

    ci_df = bootstrap_transition_ci(trans)
    ci_df.to_csv(OUT_TRANSITION_CI, index=False)

    plot_transition_matrix(mat, OUT_FIG)

    note = render_note(mat, ci_df)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved state detail:", OUT_STATE_DETAIL)
    print("[OK] Saved transition matrix:", OUT_TRANSITION)
    print("[OK] Saved transition CI:", OUT_TRANSITION_CI)
    print("[OK] Saved figure:", OUT_FIG)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Transition Matrix ===")
    print(mat.round(3).to_string())


if __name__ == "__main__":
    main()