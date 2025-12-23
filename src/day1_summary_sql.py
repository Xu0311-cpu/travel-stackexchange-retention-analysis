# src/day1_summary_sql.py
from __future__ import annotations
import os
import duckdb

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_PATH = os.path.join(PROJECT_ROOT, "data", "day1_dau_by_community.csv")

con = duckdb.connect()

# 1) 把CSV读成一张表（名字叫 dau_by_comm）
con.execute(f"""
    CREATE OR REPLACE TABLE dau_by_comm AS
    SELECT * FROM read_csv_auto('{IN_PATH}');
""")

print("=== (1) Total DAU by day (sum across communities) ===")
daily_total = con.execute("""
    SELECT event_date, SUM(dau) AS total_dau
    FROM dau_by_comm
    GROUP BY event_date
    ORDER BY event_date;
""").df()
print(daily_total.to_string(index=False))

print("\n=== (2) Avg DAU by community (top communities) ===")
avg_by_comm = con.execute("""
    SELECT community, AVG(dau) AS avg_dau
    FROM dau_by_comm
    GROUP BY community
    ORDER BY avg_dau DESC;
""").df()
print(avg_by_comm.to_string(index=False))

print("\n=== (3) Best day vs Worst day (by total_dau) ===")
best_worst = con.execute("""
    WITH daily AS (
      SELECT event_date, SUM(dau) AS total_dau
      FROM dau_by_comm
      GROUP BY event_date
    ),
    max_day AS (
      SELECT * FROM daily ORDER BY total_dau DESC LIMIT 1
    ),
    min_day AS (
      SELECT * FROM daily ORDER BY total_dau ASC LIMIT 1
    )
    SELECT 'max' AS type, event_date, total_dau FROM max_day
    UNION ALL
    SELECT 'min' AS type, event_date, total_dau FROM min_day;
""").df()

print(best_worst.to_string(index=False))

# （可选）把摘要也保存成CSV，方便你写notes时复制数字
OUT_DIR = os.path.join(PROJECT_ROOT, "data")
daily_total.to_csv(os.path.join(OUT_DIR, "summary_daily_total.csv"), index=False)
avg_by_comm.to_csv(os.path.join(OUT_DIR, "summary_avg_by_comm.csv"), index=False)
best_worst.to_csv(os.path.join(OUT_DIR, "summary_best_worst_day.csv"), index=False)

print("\n[OK] Saved summary CSVs to data/:")
print(" - data/summary_daily_total.csv")
print(" - data/summary_avg_by_comm.csv")
print(" - data/summary_best_worst_day.csv")
