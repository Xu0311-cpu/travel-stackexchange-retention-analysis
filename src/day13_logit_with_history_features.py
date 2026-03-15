import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, confusion_matrix

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")

OUT_MODEL_DATA = os.path.join(PROJECT_ROOT, "data", "day13_model_data_with_history.csv")
OUT_COEF = os.path.join(PROJECT_ROOT, "data", "day13_logit_coefficients.csv")
OUT_PRED = os.path.join(PROJECT_ROOT, "data", "day13_logit_predictions.csv")
OUT_COMPARE = os.path.join(PROJECT_ROOT, "data", "day13_day12_vs_day13_metrics.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day13_pred_prob_by_history_active_days.png")
OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day13.md")

TRAVEL = "travel"


# =========================
# Step 1: Build daily panel
# =========================
def classify_state(day_user_df: pd.DataFrame) -> str:
    if len(day_user_df) == 0:
        return "inactive"

    n_events = len(day_user_df)
    actions = set(day_user_df["action"].tolist())

    if n_events == 1 and actions == {"view"}:
        return "view_only"

    return "engaged"


def build_daily_panel(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
    df_t = df[df["community"] == TRAVEL].copy()

    all_users = sorted(df_t["user_id"].unique())
    all_dates = pd.date_range(df_t["event_date"].min(), df_t["event_date"].max(), freq="D").date

    grouped = {
        (d, u): g.copy()
        for (d, u), g in df_t.groupby(["event_date", "user_id"])
    }

    rows = []
    for d in all_dates:
        for u in all_users:
            day_user_df = grouped.get((d, u), pd.DataFrame(columns=df_t.columns))

            state = classify_state(day_user_df)
            n_events = len(day_user_df)
            is_active_today = int(n_events > 0)
            is_engaged_today = int(state == "engaged")

            rows.append([
                d,
                u,
                state,
                n_events,
                is_active_today,
                is_engaged_today
            ])

    panel = pd.DataFrame(
        rows,
        columns=[
            "date", "user_id", "state", "n_events_today",
            "is_active_today", "is_engaged_today"
        ]
    )
    return panel


# =========================
# Step 2: Add history features
# =========================
def add_history_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["user_id", "date"]).copy()

    # 过去3天（含今天）的活跃天数 / engaged天数 / 总事件数
    panel["past_3d_active_days"] = (
        panel.groupby("user_id")["is_active_today"]
        .rolling(window=3, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    panel["past_3d_engaged_days"] = (
        panel.groupby("user_id")["is_engaged_today"]
        .rolling(window=3, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    panel["past_3d_total_events"] = (
        panel.groupby("user_id")["n_events_today"]
        .rolling(window=3, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    return panel


# =========================
# Step 3: Add label
# =========================
def add_next_day_label(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["user_id", "date"]).copy()

    panel["next_day_active"] = (
        panel.groupby("user_id")["is_active_today"].shift(-1)
    )

    panel = panel.dropna(subset=["next_day_active"]).copy()
    panel["next_day_active"] = panel["next_day_active"].astype(int)

    return panel


# =========================
# Step 4: Train / test split by time
# =========================
def train_test_split_by_time(model_df: pd.DataFrame):
    unique_dates = sorted(model_df["date"].unique())
    split_idx = int(len(unique_dates) * 0.7)
    split_date = unique_dates[split_idx]

    train_df = model_df[model_df["date"] < split_date].copy()
    test_df = model_df[model_df["date"] >= split_date].copy()

    return train_df, test_df, split_date


# =========================
# Step 5: Fit logistic regression
# =========================
def fit_logit(train_df: pd.DataFrame, test_df: pd.DataFrame):
    feature_cols = [
        "state",
        "is_active_today",
        "is_engaged_today",
        "past_3d_active_days",
        "past_3d_engaged_days",
        "past_3d_total_events"
    ]

    train_x = pd.get_dummies(
        train_df[feature_cols],
        columns=["state"],
        drop_first=True
    )
    test_x = pd.get_dummies(
        test_df[feature_cols],
        columns=["state"],
        drop_first=True
    )

    train_x, test_x = train_x.align(test_x, join="left", axis=1, fill_value=0)

    y_train = train_df["next_day_active"]
    y_test = test_df["next_day_active"]

    model = LogisticRegression(max_iter=1000)
    model.fit(train_x, y_train)

    train_pred_prob = model.predict_proba(train_x)[:, 1]
    test_pred_prob = model.predict_proba(test_x)[:, 1]

    train_pred = (train_pred_prob >= 0.5).astype(int)
    test_pred = (test_pred_prob >= 0.5).astype(int)

    metrics = {
        "train_auc": roc_auc_score(y_train, train_pred_prob),
        "test_auc": roc_auc_score(y_test, test_pred_prob),
        "train_acc": accuracy_score(y_train, train_pred),
        "test_acc": accuracy_score(y_test, test_pred),
        "test_cm": confusion_matrix(y_test, test_pred)
    }

    coef_df = pd.DataFrame({
        "feature": train_x.columns,
        "coefficient": model.coef_[0]
    }).sort_values("coefficient", ascending=False)

    pred_df = test_df.copy()
    pred_df["pred_prob"] = test_pred_prob
    pred_df["pred_label"] = test_pred

    return coef_df, pred_df, metrics


# =========================
# Step 6: Compare with Day12
# =========================
def build_compare_table(metrics_day13: dict) -> pd.DataFrame:
    # 这里手动填入 Day12 的结果（你当前项目里已经跑出来）
    day12 = {
        "model": "day12_baseline",
        "train_auc": 0.505,
        "test_auc": 0.462,
        "train_acc": 0.878,
        "test_acc": 0.850
    }

    day13 = {
        "model": "day13_with_history",
        "train_auc": metrics_day13["train_auc"],
        "test_auc": metrics_day13["test_auc"],
        "train_acc": metrics_day13["train_acc"],
        "test_acc": metrics_day13["test_acc"]
    }

    compare_df = pd.DataFrame([day12, day13])
    return compare_df


# =========================
# Step 7: Plot
# =========================
def plot_pred_prob_by_history(pred_df: pd.DataFrame, out_path: str):
    plot_df = (
        pred_df.groupby("past_3d_active_days")["pred_prob"]
        .mean()
        .reset_index()
        .sort_values("past_3d_active_days")
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(plot_df["past_3d_active_days"], plot_df["pred_prob"], marker="o")

    ax.set_title("Day13: Predicted Next-Day Active Probability by Past 3D Active Days")
    ax.set_xlabel("Past 3-day active days")
    ax.set_ylabel("Predicted probability")

    for _, row in plot_df.iterrows():
        ax.text(row["past_3d_active_days"], row["pred_prob"] + 0.01, f"{row['pred_prob']:.2f}", ha="center")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 8: Note
# =========================
def render_note(split_date, coef_df, metrics, compare_df, pred_df) -> str:
    cm = metrics["test_cm"]
    top_coef = coef_df.iloc[0]
    bottom_coef = coef_df.iloc[-1]

    state_prob = (
        pred_df.groupby("state")["pred_prob"]
        .mean()
        .reindex(["inactive", "view_only", "engaged"])
        .reset_index()
    )

    hist_prob = (
        pred_df.groupby("past_3d_active_days")["pred_prob"]
        .mean()
        .reset_index()
        .sort_values("past_3d_active_days")
    )

    md = f"""# Day13

## 研究问题
Day12 的 baseline 模型只使用了“今天的状态”，结果几乎没有预测力。  
因此 Day13 的目标是：

> 引入 **短期历史特征**，看模型是否能更好地预测用户次日是否活跃。

## 新增特征
相比 Day12，Day13 增加了以下历史特征（都只使用今天及之前的信息）：

- `past_3d_active_days`：过去 3 天里活跃了几天
- `past_3d_engaged_days`：过去 3 天里 engaged 了几天
- `past_3d_total_events`：过去 3 天总事件数

这些特征的核心想法是：  
**用户的短期活跃惯性，可能比“今天这一天是什么状态”更有预测价值。**

## 方法
- 标签：`next_day_active`
- 模型：逻辑回归
- 切分方式：按时间切分训练集 / 测试集
- 训练 / 测试分界日期：**{split_date}**

## Day12 vs Day13 对比
{compare_df.to_markdown(index=False)}

## Day13 模型结果
- Train AUC: **{metrics['train_auc']:.3f}**
- Test AUC: **{metrics['test_auc']:.3f}**
- Train Accuracy: **{metrics['train_acc']:.3f}**
- Test Accuracy: **{metrics['test_acc']:.3f}**

### 测试集混淆矩阵
|                | Pred 0 | Pred 1 |
|----------------|--------|--------|
| Actual 0       | {cm[0,0]} | {cm[0,1]} |
| Actual 1       | {cm[1,0]} | {cm[1,1]} |

## 系数解释
- 正向影响最强的特征：**{top_coef['feature']}**（coef = {top_coef['coefficient']:.3f}）
- 负向影响最强的特征：**{bottom_coef['feature']}**（coef = {bottom_coef['coefficient']:.3f}）

## 按状态的平均预测概率
{state_prob.to_markdown(index=False)}

## 按过去 3 天活跃天数的平均预测概率
{hist_prob.to_markdown(index=False)}

## 核心理解
Day13 的重点不在于把模型变复杂，而在于证明一件事：

> 当 baseline 没有足够预测力时，应该优先检查“特征是否太弱”，而不是盲目换更复杂模型。

如果 Day13 的表现优于 Day12，说明：
- 短期历史确实提供了更多信息
- 用户行为具有“惯性”
- 行为链条比单日状态更重要

如果 Day13 依然很弱，也同样有意义：
- 说明 toy 数据本身信号有限
- 也提示你真实项目必须依赖更真实、更丰富的数据

## 方法边界
- 依旧是逻辑回归 baseline，不追求最优效果
- 特征仍然较少，没有引入更长窗口或更细行为序列
- toy 数据更适合方法训练，不适合作为申请主项目

## 下一步
Day14 可以进入两个方向：
1. 做更强的特征（例如过去 7 天、行为序列特征）
2. 正式启动真实公开数据项目，把这条分析链迁移过去
"""
    return md


# =========================
# Main
# =========================
def main():
    df = pd.read_csv(DATA_PATH)

    panel = build_daily_panel(df)
    panel = add_history_features(panel)
    model_df = add_next_day_label(panel)
    model_df.to_csv(OUT_MODEL_DATA, index=False)

    train_df, test_df, split_date = train_test_split_by_time(model_df)

    coef_df, pred_df, metrics = fit_logit(train_df, test_df)

    coef_df.to_csv(OUT_COEF, index=False)
    pred_df.to_csv(OUT_PRED, index=False)

    compare_df = build_compare_table(metrics)
    compare_df.to_csv(OUT_COMPARE, index=False)

    plot_pred_prob_by_history(pred_df, OUT_FIG)

    note = render_note(split_date, coef_df, metrics, compare_df, pred_df)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved model data:", OUT_MODEL_DATA)
    print("[OK] Saved coefficients:", OUT_COEF)
    print("[OK] Saved predictions:", OUT_PRED)
    print("[OK] Saved compare table:", OUT_COMPARE)
    print("[OK] Saved figure:", OUT_FIG)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Metrics ===")
    print(f"Train AUC: {metrics['train_auc']:.3f}")
    print(f"Test AUC : {metrics['test_auc']:.3f}")
    print(f"Train ACC: {metrics['train_acc']:.3f}")
    print(f"Test ACC : {metrics['test_acc']:.3f}")

    print("\n=== Coefficients ===")
    print(coef_df.to_string(index=False))


if __name__ == "__main__":
    main()