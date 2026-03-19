# Day19

## 研究目标
Day19 进一步检验：  
> **不同动作类型的留存差异，是否在社区不同发展阶段中仍然成立？**

为此，将 Travel 社区划分为三个阶段：
- `early_stage`：2011–2014
- `middle_stage`：2015–2019
- `late_stage`：2020–2024

---

## 分阶段动作留存结果
| stage        | action_segment        |   base_users |   retained_users |   d1_retention |
|:-------------|:----------------------|-------------:|-----------------:|---------------:|
| early_stage  | comment_only_user_day |        15186 |             4305 |       0.283485 |
| early_stage  | question_user_day     |         7119 |             1985 |       0.278831 |
| early_stage  | answer_user_day       |        12703 |             5069 |       0.39904  |
| middle_stage | comment_only_user_day |        66275 |            17901 |       0.270102 |
| middle_stage | question_user_day     |        27072 |             5542 |       0.204713 |
| middle_stage | answer_user_day       |        34091 |            14815 |       0.434572 |
| late_stage   | comment_only_user_day |        32221 |             7928 |       0.246051 |
| late_stage   | question_user_day     |         8541 |             2118 |       0.24798  |
| late_stage   | answer_user_day       |        11715 |             4717 |       0.402646 |

---

## 跨阶段汇总
| action_segment        |   mean_retention |   min_retention |   max_retention |
|:----------------------|-----------------:|----------------:|----------------:|
| answer_user_day       |         0.412086 |        0.39904  |        0.434572 |
| comment_only_user_day |         0.266546 |        0.246051 |        0.283485 |
| question_user_day     |         0.243842 |        0.204713 |        0.278831 |

---

## 今日核心观察
1. `answer_user_day` 在不同阶段中的留存水平分别为：
| stage        |   d1_retention |
|:-------------|---------------:|
| early_stage  |       0.39904  |
| middle_stage |       0.434572 |
| late_stage   |       0.402646 |

2. `comment_only_user_day` 在不同阶段中的留存水平分别为：
| stage        |   d1_retention |
|:-------------|---------------:|
| early_stage  |       0.283485 |
| middle_stage |       0.270102 |
| late_stage   |       0.246051 |

3. `question_user_day` 在不同阶段中的留存水平分别为：
| stage        |   d1_retention |
|:-------------|---------------:|
| early_stage  |       0.278831 |
| middle_stage |       0.204713 |
| late_stage   |       0.24798  |

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
