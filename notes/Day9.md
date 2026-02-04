# Day9 – 控制活跃度混杂：分层验证 view+comment 是否仍更高回访

## 1. 为什么要做分层
Day8 发现 travel 内 view+comment 的次日回访率高于 view-only，
但可能是“更活跃的用户更愿意评论”的自选择（confounding）导致。
因此 Day9 用“当天在 travel 的事件数”作为活跃度 proxy，分层后再比较两组回访率。

## 2. 分层规则
以用户在 day0 的 travel 社区事件数分层：
- L1_1event：当天在 travel 只有 1 个事件（轻度）
- L2_2events：当天在 travel 有 2 个事件（中度）
- L3_3plus：当天在 travel 有 3 个及以上事件（重度）

分析对象：仅保留 day0 在 travel 中发生过 view 的用户  
分组：
- Group A（view-only）：view=1 且 comment=0
- Group B（view+comment）：view=1 且 comment=1  
Outcome：次日是否回到 travel（任意行为）

## 3. 分层后的 aggregated 结果（核心）
- L1_1event：
  - view-only：a_base=84，a_rate=0.143（12/84）
  - view+comment：无样本（NaN）
  - 含义：轻度用户几乎不发生 comment，无法验证 comment 对该层的影响

- L2_2events：
  - view-only：a_base=34，a_rate=0.147（5/34），CI≈[0.064, 0.301]
  - view+comment：b_base=12，b_rate=0.333（4/12），CI≈[0.138, 0.609]
  - lift=+0.186，ratio≈2.27
  - 含义：在中度活跃层，comment 与更高次日回访相关（但样本仍偏小）

- L3_3plus：
  - view-only：a_base=10，a_rate=0.100（1/10）
  - view+comment：b_base=1，b_rate=0.000（0/1）
  - 含义：样本过小，无法解释方向（不应下结论）

## 4. 结论（用可能/更可能）
- Day8 的总体差异更可能来自“活跃度差异/自选择”，而不是 comment 的普遍提升效果：
  - 因为轻度用户（L1）几乎没有 comment 样本，comment 组主要出现在更活跃的层（L2/L3）
- comment 更可能是“中度活跃用户的高意愿信号”，在该人群中与更高回访相关
- 对轻度用户来说，当前数据无法证明“推 comment 提升留存”，因为 comment 行为本身并未发生（样本为 0）

## 5. 运营含义（更可执行）
- 如果目标是提升整体留存，单纯“推评论”可能不会覆盖大多数轻度用户
- 更合理的路径是：
  1) 先提升轻度用户的基础参与（从 view → 轻互动），让 comment 在 L1 中出现（扩大 comment base）
  2) 同时在 L2 人群中做 comment 引导实验（因为该层已经出现正向关联信号）
  3) 防止垃圾互动：若为了拉高评论量而强推，可能引入无意义评论，反而损害体验

## 6. 下一步（Day10）
Day10 将把策略拆成两个问题验证：
A) “如何让 L1 产生更多 comment”（提升 base）：设计低门槛 comment 引导，并观察 comment base 是否上升  
B) “comment 是否真的带来增量回访”（更像因果验证）：在 L2 层内做更严格对照（例如按 day0 事件数/活跃度进一步匹配）
