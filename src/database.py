import sqlite3
import os

DB_PATH = "luse_v2.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def create_tables(conn=None):
    close_conn = False
    if conn is None:
        conn = get_conn()
        close_conn = True
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        date TEXT,
        ticker TEXT,
        close_price REAL,
        daily_change REAL,
        traded_vol INTEGER,
        bid_vol INTEGER,
        bid_price REAL,
        ask_price REAL,
        ask_vol INTEGER,
        is_index INTEGER DEFAULT 0,
        is_off_market INTEGER DEFAULT 0,
        source TEXT,
        PRIMARY KEY (date, ticker)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lasi (
        date TEXT PRIMARY KEY,
        close REAL,
        change REAL
    )
    """)
    for sql in [
        "ALTER TABLE prices ADD COLUMN is_index INTEGER DEFAULT 0",
        "ALTER TABLE prices ADD COLUMN is_off_market INTEGER DEFAULT 0",
        "ALTER TABLE prices ADD COLUMN traded_vol INTEGER DEFAULT 0"
    ]:
        try: cur.execute(sql)
        except: pass
    cur.execute("UPDATE prices SET is_index=1 WHERE ticker='LASI'")
    conn.commit()
    if close_conn: conn.close()

if __name__ == "__main__":
    os.makedirs("posts", exist_ok=True)
    conn = get_conn()
    create_tables(conn)
    conn.close()
    print("DB ready V2.1")
