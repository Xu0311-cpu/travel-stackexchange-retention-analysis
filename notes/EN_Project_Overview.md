# Project Overview

## Executive Summary
This project analyzes real user behavior data from Travel Stack Exchange to understand how **community scale**, **short-term retention**, and **participation depth** interact over time.

Using **414,791 real events**, **40,600 users**, and **214,923 user-days** from 2011 to 2024, the project finds that:

- **community growth and user stickiness did not peak at the same time**
- **answer-oriented contribution had the strongest next-day retention (~42%)**
- this retention advantage remained **stable under large base sizes, bootstrap confidence intervals, and stage-level comparisons**

The project frames community quality as a **behavioral-depth problem**, rather than simply an activity-volume problem.

---

## 1. Project Title
**Community Retention & Behavioral Depth Analysis on Travel Stack Exchange**

A real-world community analytics project built on public behavioral data from Travel Stack Exchange to study how **activity scale**, **short-term retention**, and **participation depth** evolve over time.

---

## 2. Core Business Questions
This project focuses on four questions:

1. How large and active is the community over time?
2. Does peak community scale coincide with peak short-term retention?
3. Are different participation behaviors associated with meaningfully different retention outcomes?
4. Are those differences stable across community stages?

---

## 3. Dataset Summary
**Source:** Travel Stack Exchange public data dump  
**Time range:** 2011-06-21 to 2024-03-31

### Data size
- **414,791** real community events
- **40,600** users
- **214,923** user-days

### Event types
- `question`
- `answer`
- `comment`

---

## 4. Analytical Workflow

### Phase 1 — Method Building on Toy Data
The project first used a toy dataset to establish a full analytical chain and train methodological discipline.

**What was built in this phase:**
- D1 retention calculation
- action-level comparison
- confidence interval estimation
- base-size sensitivity checks
- cohort comparison
- stratified validation
- transition analysis
- baseline predictive modeling

**Purpose:**  
To build a rigorous analytical workflow before switching to real public data.

### Phase 2 — Real-World Community Analysis
The workflow was then migrated to the real Travel Stack Exchange dataset.

**Main steps:**
1. Build raw event table from XML
2. Construct user-day behavioral table
3. Measure DAU and D1 retention
4. Analyze monthly activity and retention structure
5. Segment behavior into participation-depth groups
6. Validate retention differences using base size, confidence intervals, and stage comparisons

---

## 5. Key Methods

### 5.1 User-Day Table Construction
Raw event logs were aggregated into a `user_id × event_date` structure with daily counts of:
- total events
- question count
- answer count
- comment count

This created the analytical base for all retention and behavior analyses.

### 5.2 Core Metrics
The project measured:
- **DAU**
- **D1 retention**
- **MAU**
- **monthly average DAU**
- **monthly average D1 retention**

### 5.3 Behavioral Segmentation
To better represent participation depth, user-days were segmented as:
- `question_user_day`: at least one question
- `answer_user_day`: at least one answer
- `comment_only_user_day`: comment activity without question or answer

These segments were used to approximate three participation modes:
- **demand expression**
- **lightweight interaction**
- **high-value contribution**

### 5.4 Stability Validation
To avoid over-interpreting point estimates, the project added:
- base size checks
- daily volatility analysis
- bootstrap confidence intervals
- cross-stage comparison

---

## 6. Key Findings

### 6.1 Growth and Stickiness Did Not Peak at the Same Time
Monthly activity and monthly retention did not peak in the same period.

- **Peak MAU:** 2019-05
- **Peak monthly average DAU:** 2016-08
- **Peak monthly average D1 retention:** 2011-06

**Interpretation:**  
Community growth and user stickiness are related, but not equivalent.

### 6.2 Contribution-Oriented Behavior Had the Strongest Retention
Action-level D1 retention showed a clear hierarchy:

- **answer_user_day:** **42.0%**
- **comment_only_user_day:** **26.5%**
- **question_user_day:** **22.6%**

**Interpretation:**  
Deeper content contribution was much more strongly associated with short-term retention than lightweight interaction or demand-driven participation.

### 6.3 The Difference Was Stable Under Large Base Sizes and CI Checks
The retention gap remained stable with large sample sizes:

- **answer:** 58,509 base user-days
- **comment-only:** 113,682 base user-days
- **question:** 42,732 base user-days

Bootstrap confidence intervals remained narrow:

- **answer:** [41.6%, 42.5%]
- **comment-only:** [26.2%, 26.7%]
- **question:** [22.2%, 23.0%]

### 6.4 The Pattern Also Held Across Community Stages
The project split the community timeline into:
- **early stage:** 2011–2014
- **middle stage:** 2015–2019
- **late stage:** 2020–2024

Across all three stages, `answer_user_day` remained the highest-retention behavior segment.

**Interpretation:**  
This makes the main finding more than a one-period observation — it becomes a cross-stage structural insight.

---

## 7. Business Interpretation
If Travel Stack Exchange is viewed as a community product, this project suggests:

- not all activity has equal retention quality
- contribution-oriented behavior is more strongly associated with user stickiness than simple activity volume
- growth teams should distinguish between:
  - demand expression
  - lightweight interaction
  - high-value contribution

### Core takeaway
> Community quality should not be measured only by activity scale, but also by the depth and type of participation behind that activity.

---

## 8. Why This Project Matters
This project demonstrates more than coding or dashboarding ability. It shows a full analytical workflow:

- building datasets from raw public data
- defining meaningful product metrics
- separating scale from stickiness
- connecting behavior to retention
- checking stability before drawing conclusions
- translating results into product and growth interpretation

---

## 9. Limitations
This is still an observational project, so the findings should be interpreted carefully.

### Key limitations
- no direct view/impression logs are available in the public dump
- behavior-retention relationships are correlational, not causal
- answer users may differ systematically from question users in skill, intent, or familiarity
- stage definitions are analytically useful but manually defined

---

## 10. Future Extensions
Possible next steps include:
- longer retention windows (D3, D7, D14)
- user-level stratification by tenure or activity frequency
- cohort-based comparison across entry periods
- simple causal-approximation methods
- contributor lifecycle analysis

---

## 11. Skills Demonstrated
This project demonstrates capability in:
- data cleaning and restructuring
- XML parsing
- behavioral analytics
- retention analysis
- time-series analysis
- segmentation logic
- bootstrap confidence intervals
- structured business interpretation
- reproducible project organization

---

## 12. Reproducibility
Core scripts are organized under `src/` and follow a step-by-step analytical progression.

### Main real-data workflow
- raw XML parsing and event-table construction
- user-day table generation
- DAU and D1 retention calculation
- monthly time-series structure analysis
- action-level retention analysis
- retention stability validation
- stage-level comparison

---

## 13. Author Note
This project was built as part of a structured capability reconstruction plan aimed at developing stronger foundations in:

- analytical logic
- retention thinking
- statistical stability judgment
- behavioral segmentation
- end-to-end project storytelling

