# Day8 – Travel 对照验证：comment 是否与次日回访相关？

## 1. 问题
在 travel 社区内，我希望验证：在“同样 view 过的人”中，当天发生 comment 的用户，次日回到 travel 的比例是否更高。

重点：这里只验证“相关性”，不下因果结论。

## 2. 分组（对照设计）
- Group A（view-only）：当天在 travel 有 view，但没有 comment
- Group B（view+comment）：当天在 travel 有 view，且发生 comment
- Outcome：次日是否回到 travel（任意行为）

## 3. Aggregated 结果（更稳定口径）
- view-only：base=128，returned=18，rate=0.141
- view+comment：base=13，returned=4，rate=0.308
- lift（B-A）= +0.167
- ratio（B/A）= 2.188

解释：在 travel 中，发生 comment 的用户次日回访比例更高（约 2.19 倍）。

## 4. 置信区间（不确定性说明）
使用 Wilson 95% CI：
- view-only CI：[0.091, 0.211]（n=128）
- view+comment CI：[0.127, 0.576]（n=13）

观察：
- view+comment 的区间很宽，说明样本较小导致估计不稳定
- 两组 CI 存在重叠，提示差异目前不足以形成强结论

## 5. 暂定解释（不下因果）
更可能的解释是：comment 是“更高投入/更高意愿”的信号，
因此 comment 用户本身可能更活跃、更愿意回访，而不是“comment 直接导致回访”。

但该结果仍然支持一个策略方向：在 travel 社区中，comment 可能是值得引导和验证的互动路径。

## 6. 运营含义（可执行版本）
- 当前证据支持“comment 与回访相关”，可以作为增长实验方向
- 但不建议直接重押或把它当作确定因果机制
- 更合理的做法：
  1) 以 view 人群为入口扩大样本
  2) 对 comment 引导做轻量实验（入口曝光、评论提示、优质评论示例/置顶）
  3) 同时监控垃圾互动风险（短评、重复评论等代理指标）

## 7. 下一步（Day9）
目标：提高证据稳健性，回答“是否只是活跃度差异造成的假象”。
计划：
- 在 travel 内做活跃度分层（例如：当天事件数/当天活跃社区数分层）
- 在同一活跃度层内比较 view-only vs view+comment 的次日回访差异
如果差异仍存在，策略可信度显著提升；否则说明差异更可能来自用户自选择（更活跃的人更爱评论）。
