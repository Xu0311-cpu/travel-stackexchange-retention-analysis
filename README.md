# Community Retention & Behavioral Depth Analysis on Travel Stack Exchange

A real-world community analytics project built on public behavioral data from Travel Stack Exchange to study how **community scale**, **short-term retention**, and **participation depth** interact over time.

## Executive Summary

Using **414,791 real events**, **40,600 users**, and **214,923 user-days** from **2011 to 2024**, this project analyzed how user behavior quality relates to retention in a knowledge-sharing community.

The project found that:

- **community growth and user stickiness did not peak at the same time**
- **answer-oriented contribution had the strongest next-day retention (~42%)**
- this retention advantage remained **stable across large base sizes, bootstrap confidence intervals, and early/middle/late community stages**

The core insight is:

> **Community quality should not be measured only by activity scale, but also by the depth and type of participation behind that activity.**

---

## Business Questions

This project focuses on four questions:

1. How large and active is the community over time?
2. Does peak community scale coincide with peak short-term retention?
3. Are different participation behaviors associated with meaningfully different retention outcomes?
4. Are those differences stable across community stages?

---

## Dataset Summary

- **Source:** Travel Stack Exchange public data dump
- **Time range:** 2011-06-21 to 2024-03-31
- **Events:** 414,791
- **Users:** 40,600
- **User-days:** 214,923

### Event types
- `question`
- `answer`
- `comment`

---

## Analytical Workflow

### Phase 1 — Method Building on Toy Data
A toy dataset was first used to establish a rigorous analytical workflow, including:

- D1 retention calculation
- action-level comparison
- confidence interval estimation
- base-size sensitivity checks
- cohort comparison
- stratified validation
- transition analysis
- baseline predictive modeling

### Phase 2 — Real-World Community Analysis
The workflow was then migrated to the real Travel Stack Exchange dataset:

1. Build raw event table from XML
2. Construct user-day behavioral table
3. Measure DAU and D1 retention
4. Analyze monthly activity and retention structure
5. Segment behavior into participation-depth groups
6. Validate retention differences using base size, bootstrap CI, and stage comparisons

---

## Key Findings

### 1. Growth and Stickiness Did Not Peak at the Same Time
- **Peak MAU:** 2019-05
- **Peak monthly average DAU:** 2016-08
- **Peak monthly average D1 retention:** 2011-06

This suggests that **community growth and user stickiness are related, but not equivalent**.

### 2. Contribution-Oriented Behavior Had the Strongest Retention
Action-level D1 retention showed a clear hierarchy:

- **answer_user_day:** **42.0%**
- **comment_only_user_day:** **26.5%**
- **question_user_day:** **22.6%**

This indicates that deeper content contribution was much more strongly associated with short-term retention than lightweight interaction or demand-driven participation.

### 3. The Difference Was Stable
The retention gap remained stable under:

- **large base sizes**
- **bootstrap confidence intervals**
- **cross-stage comparison**

For example:

- answer: **58,509** base user-days, **95% CI = [41.6%, 42.5%]**
- comment-only: **113,682** base user-days, **95% CI = [26.2%, 26.7%]**
- question: **42,732** base user-days, **95% CI = [22.2%, 23.0%]**

### 4. The Pattern Also Held Across Community Stages
The community timeline was split into:

- **early stage:** 2011–2014
- **middle stage:** 2015–2019
- **late stage:** 2020–2024

Across all three stages, `answer_user_day` remained the highest-retention behavior segment.

---

## Business Interpretation

If Travel Stack Exchange is viewed as a community product, this project suggests:

- not all activity has equal retention quality
- contribution-oriented behavior is more strongly associated with user stickiness than simple activity volume
- growth teams should distinguish between:
  - demand expression
  - lightweight interaction
  - high-value contribution

---

## Repository Structure

```text
community_retention/
├── data/       # processed datasets and outputs
├── figures/    # exported charts
├── notes/      # analysis notes and delivery documents
├── src/        # analysis scripts
├── .gitignore
└── README.md