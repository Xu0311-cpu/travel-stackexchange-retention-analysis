# 2-Minute Project Pitch

## English Version

I built a real-world community analytics project using public behavioral data from Travel Stack Exchange.

The project started from a simple question:  
**Does community growth necessarily mean stronger user stickiness, and which behaviors are actually associated with high-quality retention?**

To answer this, I first transformed raw XML data into a structured **user-day dataset**, covering **414K+ real events**, **40.6K users**, and **214.9K user-days** from **2011 to 2024**.

Then I analyzed the community from three layers.

First, I measured **DAU and D1 retention** and found that the months with the highest activity scale did **not** coincide with the months with the highest short-term retention. That suggested that growth and stickiness are related, but not the same thing.

Second, I segmented user participation into **question**, **comment-only**, and **answer** behaviors to approximate different participation depths. I found that **answer-oriented contribution** had the strongest next-day retention at about **42%**, compared with **26.5% for comment-only** and **22.6% for question behavior**.

Third, I validated the stability of this result using **large base sizes, bootstrap confidence intervals, and stage-level comparisons**. The answer-related retention advantage remained consistent across early, middle, and late community stages.

So the main takeaway from this project is that:

**community quality should not be measured only by activity volume, but also by the depth and type of participation behind that activity.**

This project helped me practice the full workflow from **raw data construction**, to **metric definition**, to **behavioral interpretation**, and finally to **business-oriented storytelling**.

---

## 中文版

我做了一个基于 Travel Stack Exchange 真实公开行为数据的社区分析项目。

这个项目的核心问题是：  
**社区规模增长，是否真的意味着用户粘性更强？以及，哪类参与行为更接近高质量留存？**

为了解答这个问题，我先把原始 XML 数据整理成结构化的 **user-day 数据集**，覆盖了 **41 万+ 条真实行为、4.06 万名用户、21.49 万条 user-day 记录**，时间范围从 **2011 年到 2024 年**。

接着我从三个层次展开分析。

第一层，我计算了 **DAU 和 D1 retention**，发现社区活跃规模的峰值和留存峰值并不出现在同一时期。这说明“增长”和“粘性”有关，但并不等价。

第二层，我把用户行为分成了 **question、comment-only 和 answer** 三类，用来近似表示不同参与深度。结果发现，**answer 型贡献行为**的次日留存最高，约为 **42%**，明显高于 **comment-only 的 26.5%** 和 **question 的 22.6%**。

第三层，我进一步用 **大样本 base size、bootstrap 置信区间，以及早期/中期/后期阶段比较** 去验证这个差异是否稳定。结果表明，answer 行为对应更高留存这一模式在不同阶段都成立。

所以这个项目最核心的结论是：

**社区质量不能只用活动量来衡量，还要看活动背后的参与深度和参与类型。**

这个项目让我完整练习了从 **原始数据构建、指标定义、行为解释，到业务化表达** 的整条分析链。