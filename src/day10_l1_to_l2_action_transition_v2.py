import os
import numpy as np
import pandas as pd

# =========================
# Config
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_SUMMARY_1D = os.path.join(PROJECT_ROOT, "data", "day10_l1_to_l2_transition_v2_summary_1d.csv")
OUT_SUMMARY_3D = os.path.join(PROJECT_ROOT, "data", "day10_l1_to_l2_transition_v2_summary_3d.csv")
OUT_DETAIL = os.path.join(PROJECT_ROOT, "data", "day10_l1_to_l2_transition_v2_detail.csv")
OUT_REPORT = os.path.join(PROJECT_ROOT, "notes", "Day10.md")

TRAVEL = "travel"

# 分层定义（你现在用的 L1=1 event, L2=2+ events）
L1_EVENTS = 1
L2_MIN_EVENTS = 2

# 迁移窗口：1=次日，3=三日内
HORIZONS = [1, 3]

# Bootstrap
BOOTSTRAP_B = 2000
CI_ALPHA = 0.05
RANDOM_SEED = 42


# =========================
# Helpers
# =========================
def build_l1_rows(df_t: pd.DataFrame) -> pd.DataFrame:
    """
    构造 L1 用户-日样本：
    对 travel 社区的每一天，找到当天事件数=1 的用户（L1）
    记录这一天的 action（因为只有一条事件，所以就是当天 action）
    并计算：未来 h 天内是否升级到 L2（任一天在 travel 的事件数>=2）
    """
    df_t = df_t.copy()
    df_t["event_date"] = pd.to_datetime(df_t["event_date"]).dt.date
    days = sorted(df_t["event_date"].unique())

    # 预先计算：每个 user 在每个 day 的事件数（travel）
    daily_cnt = (
        df_t.groupby(["event_date", "user_id"])
        .size()
        .reset_index(name="n_events")
    )

    # 为了快速查未来几天升级：把 daily_cnt 做成字典
    # key = (date, user_id) -> n_events
    cnt_map = {(r["event_date"], r["user_id"]): int(r["n_events"]) for _, r in daily_cnt.iterrows()}

    rows = []

    for d in days:
        # 当天所有事件
        day_df = df_t[df_t["event_date"] == d]

        # 当天每个用户事件数
        cnt_today = day_df.groupby("user_id").size()

        # L1 用户
        l1_users = cnt_today[cnt_today == L1_EVENTS].index.tolist()

        for uid in l1_users:
            # 当天只有 1 条事件，因此 action 唯一
            action = day_df.loc[day_df["user_id"] == uid, "action"].iloc[0]

            # 计算未来不同 horizon 是否升级到 L2
            flags = {}
            for h in HORIZONS:
                upgraded = 0
                for k in range(1, h + 1):
                    nd = (pd.to_datetime(d) + pd.Timedelta(days=k)).date()
                    if cnt_map.get((nd, uid), 0) >= L2_MIN_EVENTS:
                        upgraded = 1
                        break
                flags[f"upgraded_to_L2_within_{h}d"] = upgraded

            rows.append([d, uid, action] + [flags[f"upgraded_to_L2_within_{h}d"] for h in HORIZONS])

    cols = ["date", "user_id", "first_action"] + [f"upgraded_to_L2_within_{h}d" for h in HORIZONS]
    return pd.DataFrame(rows, columns=cols)


def cluster_bootstrap_ci(out: pd.DataFrame, horizon_col: str) -> pd.DataFrame:
    """
    对每个 first_action 的 upgrade_rate 做 cluster bootstrap CI（按 user_id 重抽样）
    为什么按 user_id：同一个用户多天记录不是独立样本，按行抽样会让 CI 虚假变窄。
    """
    rng = np.random.default_rng(RANDOM_SEED)

    users = out["user_id"].unique()
    actions = sorted(out["first_action"].unique())

    # 真实点估计
    point = (
        out.groupby("first_action")
        .agg(l1_user_days=("user_id", "count"),
             l1_users=("user_id", "nunique"),
             upgraded=(horizon_col, "sum"))
        .reset_index()
    )
    point["upgrade_rate"] = point["upgraded"] / point["l1_users"].replace(0, np.nan)

    # bootstrap 分布
    boot_rates = {a: [] for a in actions}

    # 预先把每个用户对应的行存起来，加速
    by_user = {u: out[out["user_id"] == u] for u in users}

    for _ in range(BOOTSTRAP_B):
        sampled_users = rng.choice(users, size=len(users), replace=True)
        boot_df = pd.concat([by_user[u] for u in sampled_users], ignore_index=True)

        tmp = (
            boot_df.groupby("first_action")
            .agg(l1_users=("user_id", "nunique"),
                 upgraded=(horizon_col, "sum"))
            .reset_index()
        )
        tmp["upgrade_rate"] = tmp["upgraded"] / tmp["l1_users"].replace(0, np.nan)

        tmp_map = dict(zip(tmp["first_action"], tmp["upgrade_rate"]))
        for a in actions:
            boot_rates[a].append(tmp_map.get(a, np.nan))

    # 计算 CI
    lo_q = CI_ALPHA / 2
    hi_q = 1 - CI_ALPHA / 2

    ci_rows = []
    for a in actions:
        arr = np.array([x for x in boot_rates[a] if not np.isnan(x)])
        if len(arr) == 0:
            lo, hi = np.nan, np.nan
        else:
            lo, hi = np.quantile(arr, [lo_q, hi_q])
        ci_rows.append([a, lo, hi])

    ci = pd.DataFrame(ci_rows, columns=["first_action", "ci_low", "ci_high"])

    # 合并
    res = point.merge(ci, on="first_action", how="left")
    res = res.sort_values("upgrade_rate", ascending=False)
    return res


def render_report(out: pd.DataFrame, summary_1d: pd.DataFrame, summary_3d: pd.DataFrame) -> str:
    def df_to_md(df):
        return df.to_markdown(index=False)

    # 找出“观察到什么”最核心一句话（自动生成也可以，但保持谨慎）
    top1 = summary_1d.iloc[0]
    stmt = (
        f"- 在 travel 社区的 L1 用户中，按 first_action 分组后，"
        f"次日升级到 L2 的最高 action 是 **{top1['first_action']}**，"
        f"点估计 upgrade_rate={top1['upgrade_rate']:.3f}，"
        f"95% bootstrap CI=[{top1['ci_low']:.3f}, {top1['ci_high']:.3f}]。\n"
        f"- 注意：这只是**条件相关**（association），不能解释为“该 action 导致升级”。"
    )

    md = f"""# Day10 — L1 → L2 行为迁移（travel）

## 研究问题
在 travel 社区里，用户从 L1（当天 1 次事件）升级到 L2（未来窗口内某天 ≥2 次事件）的概率，是否与当天 first_action 有关？

## 定义
- L1：当天在 travel 的事件数 = {L1_EVENTS}
- L2：某天在 travel 的事件数 ≥ {L2_MIN_EVENTS}
- first_action：L1 当天的唯一 action（因为该日只有 1 条事件）
- 升级（upgrade）：在未来 *h* 天内（h∈{HORIZONS}），任一天达到 L2

## 方法
- 构造 L1 用户-日样本（date, user_id, first_action, upgraded_within_h）
- 按 first_action 汇总 upgrade_rate
- 用 **cluster bootstrap（按 user_id 重抽样）** 估计 95% CI  
  目的：避免同一用户多天记录导致的“CI 虚假变窄”。

## 结果摘要
{stmt}

## 结果表（h=1 day）
{df_to_md(summary_1d[['first_action','l1_users','upgraded','upgrade_rate','ci_low','ci_high']])}

## 结果表（h=3 days）
{df_to_md(summary_3d[['first_action','l1_users','upgraded','upgrade_rate','ci_low','ci_high']])}

## 因果边界（必须声明）
- 本分析是观察性数据的分组比较，只能说明“first_action 与升级相关”，不能证明因果。
- 潜在混淆：用户本身的活跃倾向、时间趋势、社区热度等都可能同时影响 action 与升级。

## 下一步（Week1 的方向）
1) 加入活跃度分层（你已经在 Day9 做过），在 L2 层内部重复这套迁移分析。  
2) 做稳健性：窗口（1d vs 3d）、阈值（L2=2+ vs 3+）、placebo（不应有效的定义）。  
3) 进入 Day11：用逻辑回归预测次日留存（严格防止数据泄漏）。
"""
    return md


# =========================
# Main
# =========================
def main():
    df = pd.read_csv(DATA_PATH)
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    df_t = df[df["community"] == TRAVEL].copy()

    # 构造 L1 样本
    out = build_l1_rows(df_t)
    out.to_csv(OUT_DETAIL, index=False)

    # 不同 horizon 的 summary + CI
    s1 = cluster_bootstrap_ci(out, "upgraded_to_L2_within_1d")
    s3 = cluster_bootstrap_ci(out, "upgraded_to_L2_within_3d")

    s1.to_csv(OUT_SUMMARY_1D, index=False)
    s3.to_csv(OUT_SUMMARY_3D, index=False)

    # 报告
    report = render_report(out, s1, s3)
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report)

    print("[OK] Saved detail:", OUT_DETAIL)
    print("[OK] Saved summary (1d):", OUT_SUMMARY_1D)
    print("[OK] Saved summary (3d):", OUT_SUMMARY_3D)
    print("[OK] Saved report:", OUT_REPORT)

    print("\n=== Top lines (1d) ===")
    print(s1[["first_action","l1_users","upgraded","upgrade_rate","ci_low","ci_high"]].to_string(index=False))

if __name__ == "__main__":
    main()