# Case Sheet Outline

## 1. Project Title
**Community Retention & Behavioral Depth Analysis | Travel Stack Exchange**

---

## 2. One-Sentence Summary
Built a real-world community analytics project using **414K+ public user actions** to study how **growth, retention, and participation depth** interact over time in a knowledge-sharing community.

---

## 3. Snapshot
- **Data source:** Travel Stack Exchange public data dump
- **Time range:** 2011-06-21 to 2024-03-31
- **Events:** 414,791
- **Users:** 40,600
- **User-days:** 214,923

---

## 4. Core Business Questions
1. Does community growth necessarily imply stronger user stickiness?
2. Which types of participation are associated with higher-quality retention?
3. Are behavior-retention differences stable across time and community stages?

---

## 5. Analytical Workflow
### Phase 1 — Method Building on Toy Data
- D1 retention calculation
- action-level comparison
- confidence interval estimation
- base-size sensitivity checks
- cohort comparison
- stratified validation
- transition analysis
- baseline predictive modeling

### Phase 2 — Real-World Community Analysis
- Build raw event table from XML
- Construct user-day behavioral table
- Measure DAU and D1 retention
- Analyze monthly activity and retention structure
- Segment behavior into participation-depth groups
- Validate differences using base size, CI, and stage comparison

---

## 6. Key Metrics
- **DAU**
- **D1 retention**
- **MAU**
- **monthly average DAU**
- **monthly average D1 retention**

---

## 7. Behavioral Segmentation
User-days were segmented into:
- `question_user_day`
- `comment_only_user_day`
- `answer_user_day`

These approximate:
- **demand expression**
- **lightweight interaction**
- **high-value contribution**

---

## 8. Key Findings

### 8.1 Growth and Stickiness Did Not Peak at the Same Time
- **Peak MAU:** 2019-05
- **Peak monthly average DAU:** 2016-08
- **Peak monthly average D1 retention:** 2011-06

**Interpretation:**  
Growth and stickiness were related, but not equivalent.

### 8.2 Contribution-Oriented Behavior Had the Strongest Retention
- **answer_user_day:** **42.0%**
- **comment_only_user_day:** **26.5%**
- **question_user_day:** **22.6%**

**Interpretation:**  
Deeper contribution behavior was much more strongly associated with short-term retention than lightweight interaction or demand-driven participation.

### 8.3 The Difference Was Stable
Large base sizes:
- answer: **58,509**
- comment-only: **113,682**
- question: **42,732**

95% bootstrap CI:
- answer: **[41.6%, 42.5%]**
- comment-only: **[26.2%, 26.7%]**
- question: **[22.2%, 23.0%]**

### 8.4 The Pattern Held Across Stages
Community stages:
- **early stage:** 2011–2014
- **middle stage:** 2015–2019
- **late stage:** 2020–2024

Across all three stages, `answer_user_day` remained the highest-retention segment.

---

## 9. Business Interpretation
If Travel Stack Exchange is viewed as a community product, this project suggests:

- not all activity has equal retention quality
- contribution-oriented behavior is more strongly associated with stickiness than simple activity volume
- teams should distinguish between:
  - demand expression
  - lightweight interaction
  - high-value contribution

### Core takeaway
> Community quality should not be measured only by activity scale, but also by the depth and type of participation behind that activity.

---

## 10. Why This Project Matters
This project demonstrates:
- dataset construction from raw public data
- metric definition with product meaning
- separation of scale vs stickiness
- action-level behavioral interpretation
- stability checks before drawing conclusions
- translation of analysis into business language

---

## 11. Recommended Figures
Use these 3 figures in the final case sheet or interview deck:

1. **Monthly activity structure**
   - MAU
   - monthly average DAU
   - monthly average D1 retention

2. **Action-level retention**
   - answer vs comment-only vs question

3. **Retention stability**
   - action-level retention with confidence intervals
   - or stage-level comparison chart

---

## 12. Resume Angle
This project can be positioned as:
- **community growth analytics**
- **retention and user behavior analysis**
- **behavioral segmentation and product interpretation**
- **real-world public data pipeline + business insight generation**

---

## 13. Interview Angle
In interviews, this project is best framed around:

### Problem
Growth does not necessarily mean stronger retention.

### Method
Build a user-day dataset from raw public data and compare activity, retention, and participation depth.

### Insight
Contribution-oriented behavior consistently aligned with higher short-term retention.

### Business Meaning
Community teams should optimize for participation quality, not just activity quantity.

---

## 14. Suggested Use
This document can be used as:
- a one-page portfolio case sheet draft
- a structure for a PDF project summary
- a speaking outline before interviews
- a source document for future slide design