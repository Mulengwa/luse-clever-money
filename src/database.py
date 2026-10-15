import sqlite3
import os

DB = "luse_v2.db"
os.makedirs("posts", exist_ok=True)

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS daily_prices (
        ticker TEXT,
        date   TEXT,
        price  REAL,
        change REAL,
        volume INTEGER
    )
""")
conn.commit()
conn.close()
print("DB ready")
