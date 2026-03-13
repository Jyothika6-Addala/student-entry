import psycopg2
import pandas as pd
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

df = pd.read_sql_query("SELECT * FROM students", conn)

today = datetime.now().strftime("%Y-%m-%d")

filename = f"students_backup_{today}.xlsx"

df.to_excel(filename, index=False)

print("Excel backup created:", filename)

conn.close()