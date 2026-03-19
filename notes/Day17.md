# Day17

## 研究目标
Day17 把 toy 项目里的“按 action 看留存”正式迁移到真实 Travel 数据。

核心问题是：

> 在真实社区里，不同类型的参与行为，是否与不同水平的次日留存相关？

---

## 行为分层定义
为了让真实数据更接近业务解释，本日将 user-day 分成三类：

- **comment_only_user_day**：当天只有 comment，没有 question / answer
- **question_user_day**：当天至少有 1 次 question
- **answer_user_day**：当天至少有 1 次 answer

这个分层可以近似理解为：
- `comment_only` = 较浅互动
- `question` = 主动发起参与
- `answer` = 更深的内容贡献

---

## 总体结果
| action_segment        |   base_users |   retained_users |   d1_retention |
|:----------------------|-------------:|-----------------:|---------------:|
| comment_only_user_day |       113682 |            30134 |       0.265073 |
| question_user_day     |        42732 |             9645 |       0.225709 |
| answer_user_day       |        58509 |            24601 |       0.420465 |

---

## 按日分布统计
| action_segment        |     mean |      std |   count |
|:----------------------|---------:|---------:|--------:|
| answer_user_day       | 0.416802 | 0.179876 |    4659 |
| comment_only_user_day | 0.273421 | 0.126646 |    4665 |
| question_user_day     | 0.250745 | 0.200091 |    4641 |

---

## 今日核心观察
- 留存最高的动作分层：**answer_user_day**，D1 retention = **0.4205**
- 留存最低的动作分层：**question_user_day**，D1 retention = **0.2257**

这说明在真实社区中，不同参与深度对应的短期回访水平并不相同。  
相比只看 overall retention，这一步更接近“行为机制分析”。

---

## 商业化解释
如果把 Travel Stack Exchange 视为一个知识社区产品，那么：

- `comment_only` 可以理解为轻互动用户
- `question` 可以理解为主动表达需求的用户
- `answer` 可以理解为贡献高价值内容的用户

因此，这一步实际上是在回答一个更接近业务的问题：

> **哪类参与行为，更有可能与次日回访和持续活跃相关？**

这个问题在社区运营、内容平台、用户增长分析里都非常常见。

---

## 方法边界
- 当前仍然是观察性分析，只能说明“行为分层与留存相关”，不能解释因果
- `answer_user_day` 和 `question_user_day` 可能存在用户能力差异、自选择偏差
- 后续仍需结合 base size、时间阶段和更严格的稳健性分析

---

## 下一步
Day18 可以继续两条线：
1. **稳健性线**：给 action retention 加上 CI / base size / 时间分段对比
2. **简历包装线**：把整个真实项目整理成“社区增长 / 用户留存分析案例”
