import sys
import pandas as pd
import duckdb
import matplotlib

print("PYTHON:", sys.version.split()[0])
print("PANDAS:", pd.__version__)
print("DUCKDB:", duckdb.__version__)
print("MATPLOTLIB:", matplotlib.__version__)
print("DAY0 CHECK: OK")
