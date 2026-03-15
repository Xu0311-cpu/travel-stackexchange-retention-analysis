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

OUT_MODEL_DATA = os.path.join(PROJECT_ROOT, "data", "day12_model_data.csv")
OUT_COEF = os.path.join(PROJECT_ROOT, "data", "day12_logit_coefficients.csv")
OUT_PRED = os.path.join(PROJECT_ROOT, "data", "day12_logit_predictions.csv")
OUT_FIG = os.path.join(PROJECT_ROOT, "figures", "day12_logit_pred_prob_by_state.png")
OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day12.md")

TRAVEL = "travel"


# =========================
# Step 1: Build daily state panel
# =========================
def classify_state(day_user_df: pd.DataFrame) -> str:
    if len(day_user_df) == 0:
        return "inactive"

    n_events = len(day_user_df)
    actions = set(day_user_df["action"].tolist())

    if n_events == 1 and actions == {"view"}:
        return "view_only"

    return "engaged"


def build_state_panel(df: pd.DataFrame) -> pd.DataFrame:
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

            rows.append([
                d,
                u,
                state,
                int(n_events > 0),
                int(state == "engaged")
            ])

    panel = pd.DataFrame(
        rows,
        columns=["date", "user_id", "state", "is_active_today", "is_engaged_today"]
    )
    return panel


# =========================
# Step 2: Create label
# =========================
def add_next_day_label(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["user_id", "date"]).copy()

    panel["next_day_active"] = (
        panel.groupby("user_id")["is_active_today"].shift(-1)
    )

    panel["next_day_state"] = (
        panel.groupby("user_id")["state"].shift(-1)
    )

    # 去掉每个用户最后一天，因为没有 next day label
    panel = panel.dropna(subset=["next_day_active"]).copy()
    panel["next_day_active"] = panel["next_day_active"].astype(int)

    return panel


# =========================
# Step 3: Train / test split by time
# =========================
def train_test_split_by_time(model_df: pd.DataFrame):
    unique_dates = sorted(model_df["date"].unique())
    split_idx = int(len(unique_dates) * 0.7)
    split_date = unique_dates[split_idx]

    train_df = model_df[model_df["date"] < split_date].copy()
    test_df = model_df[model_df["date"] >= split_date].copy()

    return train_df, test_df, split_date


# =========================
# Step 4: Fit logistic regression
# =========================
def fit_logit(train_df: pd.DataFrame, test_df: pd.DataFrame):
    train_x = pd.get_dummies(
        train_df[["state", "is_active_today", "is_engaged_today"]],
        columns=["state"],
        drop_first=True
    )
    test_x = pd.get_dummies(
        test_df[["state", "is_active_today", "is_engaged_today"]],
        columns=["state"],
        drop_first=True
    )

    # 对齐列，防止 train/test 某列缺失
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

    return model, coef_df, pred_df, metrics


# =========================
# Step 5: Plot
# =========================
def plot_pred_prob_by_state(pred_df: pd.DataFrame, out_path: str):
    plot_df = pred_df.groupby("state")["pred_prob"].mean().reindex(["inactive", "view_only", "engaged"])

    fig, ax = plt.subplots(figsize=(6, 4))
    plot_df.plot(kind="bar", ax=ax)

    ax.set_title("Day12: Predicted Next-Day Active Probability by State")
    ax.set_ylabel("Predicted probability")
    ax.set_xlabel("Today's state")

    for i, v in enumerate(plot_df.values):
        ax.text(i, v + 0.01, f"{v:.2f}", ha="center")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# =========================
# Step 6: Write note
# =========================
def render_note(split_date, coef_df, metrics, pred_df) -> str:
    cm = metrics["test_cm"]

    state_prob = (
        pred_df.groupby("state")["pred_prob"]
        .mean()
        .reindex(["inactive", "view_only", "engaged"])
        .reset_index()
    )

    top_coef = coef_df.iloc[0]
    bottom_coef = coef_df.iloc[-1]

    md = f"""# Day12

## 研究问题
在完成 Day11 的状态迁移分析后，Day12 进一步把“状态”作为建模输入，尝试预测：

> 用户在 **今天的状态** 已知的情况下，**明天是否还会活跃**？

这里把 `next_day_active` 定义为：
- 1：用户明天在 travel 社区有任意行为
- 0：用户明天在 travel 社区没有行为

## 方法
1. 先基于 user-day 构造状态面板
2. 用今天的状态与活跃特征，预测明天是否活跃
3. 使用 **逻辑回归（logistic regression）**
4. 按时间切分训练集和测试集，避免随机切分打乱时序  
   - 训练/测试分界日期：**{split_date}**

## 特征
- `state`
- `is_active_today`
- `is_engaged_today`

其中：
- `inactive` 表示今天无行为
- `view_only` 表示今天只有一次 `view`
- `engaged` 表示今天有更深参与或 2+ 次行为

## 评估结果
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
逻辑回归的系数代表：某个特征增加时，预测为“次日活跃”的倾向是增强还是减弱。

- 正向影响最强的特征：**{top_coef['feature']}**（coef = {top_coef['coefficient']:.3f}）
- 负向影响最强的特征：**{bottom_coef['feature']}**（coef = {bottom_coef['coefficient']:.3f}）

## 按状态的平均预测概率
{state_prob.to_markdown(index=False)}

## 核心理解
Day12 的意义不在于“模型多复杂”，而在于第一次把前面得到的行为结构正式转成了：

- 可预测问题
- 可解释特征
- 可评估模型

这让项目从“描述性分析”进一步推进到了“预测性分析”。

## 方法边界
- 这里只是最简逻辑回归 baseline，并不追求最优性能
- 特征非常少，因此模型解释性强，但预测力有限
- toy 数据集较小，结果只适合练分析链条，不适合做强业务结论
- 逻辑回归描述的是相关性，不代表因果效应

## 下一步
Day13 可以继续两条线：
1. 增加更丰富的行为特征（过去 3 天活跃次数、过去 3 天 engaged 次数）
2. 开始把 toy 方法迁移到真实公开数据项目
"""
    return md


# =========================
# Main
# =========================
def main():
    df = pd.read_csv(DATA_PATH)

    panel = build_state_panel(df)
    model_df = add_next_day_label(panel)
    model_df.to_csv(OUT_MODEL_DATA, index=False)

    train_df, test_df, split_date = train_test_split_by_time(model_df)

    model, coef_df, pred_df, metrics = fit_logit(train_df, test_df)

    coef_df.to_csv(OUT_COEF, index=False)
    pred_df.to_csv(OUT_PRED, index=False)

    plot_pred_prob_by_state(pred_df, OUT_FIG)

    note = render_note(split_date, coef_df, metrics, pred_df)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved model data:", OUT_MODEL_DATA)
    print("[OK] Saved coefficients:", OUT_COEF)
    print("[OK] Saved predictions:", OUT_PRED)
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