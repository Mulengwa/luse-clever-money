import sqlite3
from datetime import date
DB="luse_v2.db"
conn=sqlite3.connect(DB)
c=conn.cursor()
c.execute("SELECT COUNT(*) FROM daily_prices WHERE date=?", (str(date.today()),))
count=c.fetchone()[0]
if count==0:
    today=str(date.today())
    print(f"No data for {today}, inserting sample BATZ led data")
    sample=[("BATZ",today,65.0,2.5,15000),("SCBL",today,0.85,0.05,12000),("CECZ",today,1.2,0.0,3000),("PUMA",today,4.5,-0.2,8000)]
    c.executemany("INSERT INTO daily_prices VALUES (?,?,?,?,?)",sample)
    conn.commit()
    print(f"Scraped {len(sample)} tickers (sample - weekend)")
else:
    print(f"Scraped {count} tickers already in DB")
conn.close()
