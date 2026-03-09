# Day10 — L1 → L2 行为迁移（travel）

## 研究问题
在 travel 社区里，用户从 L1（当天 1 次事件）升级到 L2（未来窗口内某天 ≥2 次事件）的概率，是否与当天 first_action 有关？

## 定义
- L1：当天在 travel 的事件数 = 1
- L2：某天在 travel 的事件数 ≥ 2
- first_action：L1 当天的唯一 action（因为该日只有 1 条事件）
- 升级（upgrade）：在未来 *h* 天内（h∈[1, 3]），任一天达到 L2

## 方法
- 构造 L1 用户-日样本（date, user_id, first_action, upgraded_within_h）
- 按 first_action 汇总 upgrade_rate
- 用 **cluster bootstrap（按 user_id 重抽样）** 估计 95% CI  
  目的：避免同一用户多天记录导致的“CI 虚假变窄”。

## 结果摘要
- 在 travel 社区的 L1 用户中，按 first_action 分组后，次日升级到 L2 的最高 action 是 **view**，点估计 upgrade_rate=0.071，95% bootstrap CI=[0.026, 0.235]。
- 注意：这只是**条件相关**（association），不能解释为“该 action 导致升级”。

## 结果表（h=1 day）
| first_action   |   l1_users |   upgraded |   upgrade_rate |   ci_low |   ci_high |
|:---------------|-----------:|-----------:|---------------:|---------:|----------:|
| view           |         56 |          4 |      0.0714286 | 0.025641 |  0.235294 |
| comment        |         21 |          0 |      0         | 0        |  0        |
| like           |         20 |          0 |      0         | 0        |  0        |
| post           |          4 |          0 |      0         | 0        |  0        |

## 结果表（h=3 days）
| first_action   |   l1_users |   upgraded |   upgrade_rate |    ci_low |   ci_high |
|:---------------|-----------:|-----------:|---------------:|----------:|----------:|
| like           |         20 |          3 |       0.15     | 0         |  0.5      |
| view           |         56 |          8 |       0.142857 | 0.0882353 |  0.382353 |
| comment        |         21 |          0 |       0        | 0         |  0        |
| post           |          4 |          0 |       0        | 0         |  0        |

## 因果边界（必须声明）
- 本分析是观察性数据的分组比较，只能说明“first_action 与升级相关”，不能证明因果。
- 潜在混淆：用户本身的活跃倾向、时间趋势、社区热度等都可能同时影响 action 与升级。

## 下一步（Week1 的方向）
1) 加入活跃度分层（你已经在 Day9 做过），在 L2 层内部重复这套迁移分析。  
2) 做稳健性：窗口（1d vs 3d）、阈值（L2=2+ vs 3+）、placebo（不应有效的定义）。  
3) 进入 Day11：用逻辑回归预测次日留存（严格防止数据泄漏）。
