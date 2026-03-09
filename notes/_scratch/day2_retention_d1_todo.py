# src/day2_retention_d1_todo.py
from __future__ import annotations
import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_PATH = os.path.join(PROJECT_ROOT, "data", "day2_d1_retention.csv")

d = pd.read_csv(IN_PATH)

# 你要填的3行（直接照写）
avg = round(d["d1_retention"].mean(), 3)
min_row = d.loc[d["d1_retention"].idxmin()]
max_row = d.loc[d["d1_retention"].idxmax()]#idxmin() 返回的是：哪一行“最小值所在的行号（索引）”，而不是那一整行数据。d.loc[那个编号]才是把那一整行数据取出来（date / base / returned / retention）

print(f"Avg D1 retention: {avg}")
print(f"Min day: date={min_row['date']}, d1_retention={min_row['d1_retention']}, base={min_row['base_users']}, returned={min_row['returned_users']}")
print(f"Max day: date={max_row['date']}, d1_retention={max_row['d1_retention']}, base={max_row['base_users']}, returned={max_row['returned_users']}")
