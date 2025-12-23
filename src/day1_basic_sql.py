# src/day1_basic_sql.py
from __future__ import annotations
import os
import duckdb

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")
OUT_DAU = os.path.join(PROJECT_ROOT, "data", "day1_dau.csv")

con = duckdb.connect()

# 读CSV建表
con.execute(f"""
    CREATE OR REPLACE TABLE events AS
    SELECT * FROM read_csv_auto('{DATA_PATH}');
""")

total_events = con.execute("SELECT COUNT(*) FROM events;").fetchone()[0]
total_users = con.execute("SELECT COUNT(DISTINCT user_id) FROM events;").fetchone()[0]

print("=== Day1 Basic SQL Outputs ===")
print(f"Total events: {total_events:,}")
print(f"Total users : {total_users:,}")

# DAU：每天活跃用户数（当天有任何事件就算活跃）
dau_df = con.execute("""
    SELECT event_date, COUNT(DISTINCT user_id) AS dau
    FROM events
    GROUP BY event_date
    ORDER BY event_date;
""").df()

print("\nTop 10 DAU rows:")
print(dau_df.head(10).to_string(index=False))

dau_df.to_csv(OUT_DAU, index=False)
print(f"\n[OK] Saved DAU table to: {OUT_DAU}")

#COUNT(*) = 数“记录条数”
#COUNT(DISTINCT user_id) = 数“不同的人数”
#GROUP BY event_date = “按天分组再统计”

