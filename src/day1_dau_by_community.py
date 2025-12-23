# src/day1_dau_by_community.py
from __future__ import annotations
import os
import duckdb

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "toy_events.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "data", "day1_dau_by_community.csv")

con = duckdb.connect()
con.execute(f"""
    CREATE OR REPLACE TABLE events AS
    SELECT * FROM read_csv_auto('{DATA_PATH}');
""")

df = con.execute("""
    SELECT
      event_date,
      community,
      COUNT(DISTINCT user_id) AS dau
    FROM events
    GROUP BY event_date, community
    ORDER BY event_date, community;
""").df()

df.to_csv(OUT_PATH, index=False)
print(f"[OK] Saved: {OUT_PATH}")
print(df.head(12).to_string(index=False))
