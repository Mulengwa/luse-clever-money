import sqlite3, os
DB="luse_v2.db"
os.makedirs("posts", exist_ok=True)
conn=sqlite3.connect(DB)
c=conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS daily_prices (ticker TEXT, date TEXT, price REAL, change REAL, volume INTEGER)""")
conn.commit()
c.execute("SELECT COUNT(*) FROM daily_prices")
if c.fetchone()[0]==0:
    from datetime import date
    today=str(date.today())
    sample=[("BATZ",today,65.0,2.5,10000),("ZANACO",today,5.2,-0.1,5000),("CEC",today,8.1,0.3,2000)]
    c.executemany("INSERT INTO daily_prices VALUES (?,?,?,?,?)",sample)
    print(f"Seeded sample data for {today}")
conn.commit()
conn.close()
print("DB ready")
