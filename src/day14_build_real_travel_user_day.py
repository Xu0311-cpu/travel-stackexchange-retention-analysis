import os
import xml.etree.ElementTree as ET
import pandas as pd

# =========================
# Paths
# =========================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "travel_stackexchange_raw")
POSTS_XML = os.path.join(RAW_DIR, "Posts.xml")
COMMENTS_XML = os.path.join(RAW_DIR, "Comments.xml")
USERS_XML = os.path.join(RAW_DIR, "Users.xml")

OUT_EVENTS = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_events.csv")
OUT_USER_DAY = os.path.join(PROJECT_ROOT, "data", "day14_travel_real_user_day.csv")
OUT_NOTE = os.path.join(PROJECT_ROOT, "notes", "Day14.md")


# =========================
# XML helpers
# =========================
def parse_xml_rows(xml_path: str, keep_attrs: list[str]) -> pd.DataFrame:
    """
    读取 Stack Exchange dump XML（形如 <posts><row ... /></posts>）
    只保留需要的属性列
    """
    rows = []

    context = ET.iterparse(xml_path, events=("end",))
    for event, elem in context:
        if elem.tag == "row":
            row = {k: elem.attrib.get(k) for k in keep_attrs}
            rows.append(row)
            elem.clear()

    return pd.DataFrame(rows)


# =========================
# Step 1: Parse posts
# =========================
def load_posts() -> pd.DataFrame:
    """
    从 Posts.xml 提取发帖 / 回答行为
    - PostTypeId = 1 => question
    - PostTypeId = 2 => answer
    OwnerUserId 为空的匿名/已删除用户先去掉
    """
    keep = ["Id", "PostTypeId", "CreationDate", "OwnerUserId"]
    posts = parse_xml_rows(POSTS_XML, keep)

    posts = posts.dropna(subset=["OwnerUserId", "CreationDate"]).copy()

    posts["user_id"] = posts["OwnerUserId"].astype(str)
    posts["event_time"] = pd.to_datetime(posts["CreationDate"], errors="coerce")
    posts = posts.dropna(subset=["event_time"]).copy()

    posts["action"] = posts["PostTypeId"].map({
        "1": "question",
        "2": "answer"
    })

    posts = posts.dropna(subset=["action"]).copy()

    return posts[["user_id", "event_time", "action"]]


# =========================
# Step 2: Parse comments
# =========================
def load_comments() -> pd.DataFrame:
    """
    从 Comments.xml 提取 comment 行为
    """
    keep = ["Id", "CreationDate", "UserId"]
    comments = parse_xml_rows(COMMENTS_XML, keep)

    comments = comments.dropna(subset=["UserId", "CreationDate"]).copy()

    comments["user_id"] = comments["UserId"].astype(str)
    comments["event_time"] = pd.to_datetime(comments["CreationDate"], errors="coerce")
    comments = comments.dropna(subset=["event_time"]).copy()

    comments["action"] = "comment"

    return comments[["user_id", "event_time", "action"]]


# =========================
# Step 3: Build unified events
# =========================
def build_events() -> pd.DataFrame:
    posts = load_posts()
    comments = load_comments()

    events = pd.concat([posts, comments], ignore_index=True)
    events["event_date"] = events["event_time"].dt.date

    events = events.sort_values(["event_time", "user_id"]).reset_index(drop=True)
    return events


# =========================
# Step 4: Build user-day table
# =========================
def build_user_day(events: pd.DataFrame) -> pd.DataFrame:
    """
    聚合到 user-day 层级：
    - total_events
    - question_cnt
    - answer_cnt
    - comment_cnt
    - active_flag
    """
    tmp = events.copy()

    tmp["question_cnt"] = (tmp["action"] == "question").astype(int)
    tmp["answer_cnt"] = (tmp["action"] == "answer").astype(int)
    tmp["comment_cnt"] = (tmp["action"] == "comment").astype(int)

    user_day = (
        tmp.groupby(["user_id", "event_date"])
        .agg(
            total_events=("action", "count"),
            question_cnt=("question_cnt", "sum"),
            answer_cnt=("answer_cnt", "sum"),
            comment_cnt=("comment_cnt", "sum"),
        )
        .reset_index()
    )

    user_day["active_flag"] = 1

    return user_day.sort_values(["event_date", "user_id"]).reset_index(drop=True)


# =========================
# Step 5: Write note
# =========================
def render_note(events: pd.DataFrame, user_day: pd.DataFrame) -> str:
    min_date = events["event_date"].min()
    max_date = events["event_date"].max()

    action_summary = (
        events["action"]
        .value_counts()
        .rename_axis("action")
        .reset_index(name="count")
    )

    top_days = (
        user_day.groupby("event_date")["user_id"]
        .nunique()
        .reset_index(name="active_users")
        .sort_values("active_users", ascending=False)
        .head(10)
    )

    md = f"""# Day14

## 研究目标
Day14 正式从 toy 数据切换到真实公开数据。  
本日目标不是直接做分析，而是先完成真实项目的基础数据构建：

> 把 Stack Exchange 的原始 XML 转储，整理成可用于留存/迁移/建模的 `user-day` 分析表。

## 数据来源
本项目使用 Travel Stack Exchange 的公开数据转储。  
从原始 XML 中提取三类行为：

- `question`
- `answer`
- `comment`

## 今天完成的表
### 1. 事件流表
`day14_travel_real_events.csv`
- 粒度：一行 = 一个用户的一次行为
- 主要字段：
  - `user_id`
  - `event_time`
  - `event_date`
  - `action`

### 2. 用户-日期表
`day14_travel_real_user_day.csv`
- 粒度：一行 = 一个用户在某一天的聚合行为
- 主要字段：
  - `user_id`
  - `event_date`
  - `total_events`
  - `question_cnt`
  - `answer_cnt`
  - `comment_cnt`
  - `active_flag`

## 数据覆盖范围
- 起始日期：**{min_date}**
- 结束日期：**{max_date}**
- 总事件数：**{len(events):,}**
- 用户-日记录数：**{len(user_day):,}**
- 独立用户数：**{user_day['user_id'].nunique():,}**

## 行为分布
{action_summary.to_markdown(index=False)}

## 活跃用户最多的日期（Top 10）
{top_days.to_markdown(index=False)}

## 今天的意义
Day14 的关键不是业务结论，而是：
- 把真实数据成功读进来
- 明确行为口径
- 建好后续所有分析共用的底座表

这一步完成后，Day15 就可以把你前面在 toy 数据上练过的链条，正式迁移到真实数据：
- DAU
- D1 retention
- 按行为拆分
- 分层
- 迁移
- 建模

## 方法边界
- 当前只使用了 `Posts.xml` 和 `Comments.xml` 的显式行为
- 没有“view”行为，因为公开转储里通常没有浏览日志
- 因此真实项目的行为空间会和 toy 数据不同，需要在 Day15 重新定义状态与留存口径
"""
    return md


# =========================
# Main
# =========================
def main():
    # 检查原始文件是否存在
    for path in [POSTS_XML, COMMENTS_XML]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing required file: {path}\n"
                f"请先把 Travel Stack Exchange 解压后的 XML 放到 data/travel_stackexchange_raw/ 下。"
            )

    events = build_events()
    user_day = build_user_day(events)

    events.to_csv(OUT_EVENTS, index=False)
    user_day.to_csv(OUT_USER_DAY, index=False)

    note = render_note(events, user_day)
    with open(OUT_NOTE, "w", encoding="utf-8") as f:
        f.write(note)

    print("[OK] Saved events:", OUT_EVENTS)
    print("[OK] Saved user-day:", OUT_USER_DAY)
    print("[OK] Saved note:", OUT_NOTE)

    print("\n=== Summary ===")
    print(f"Date range : {events['event_date'].min()} -> {events['event_date'].max()}")
    print(f"Events     : {len(events):,}")
    print(f"User-days  : {len(user_day):,}")
    print(f"Users      : {user_day['user_id'].nunique():,}")

    print("\n=== Action counts ===")
    print(events["action"].value_counts().to_string())


if __name__ == "__main__":
    main()