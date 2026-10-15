import sqlite3, requests, re
from datetime import date
from bs4 import BeautifulSoup

DB = "luse_v2.db"
# List of all LuSE tickers - we scrape each page
TICKERS = ["ATEL","BATA","BATZ","CECZ","CHIL","CCHZ","DCZM","MAFS","NATB","PUMA","REIZ","SCBL","ZABR","ZMBF","ZCCM","ZFCO","ZMFA","ZMRE","ZNCO","ZSUG","KLRE","ZHTL","AECI","ATEL"]

headers = {"User-Agent":"Mozilla/5.0"}
today = str(date.today())

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS daily_prices (ticker TEXT, date TEXT, price REAL, change_pct REAL, volume INTEGER)")
c.execute("DELETE FROM daily_prices WHERE date=?", (today,))

count = 0
for ticker in TICKERS:
    try:
        # Try two URL patterns that afx uses
        urls = [f"https://afx.kwayisi.org/{ticker.lower()}", f"https://afx.kwayisi.org/luse:{ticker.lower()}"]
        html = None
        for url in urls:
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200 and "Close" in r.text:
                    html = r.text
                    break
            except:
                continue
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        # Find the first row of the price table: Date | Volume | Close | Change | Change%
        table = soup.find("table")
        if not table:
            continue
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        # First data row = yesterday's close
        tds = rows[1].find_all("td")
        if len(tds) < 4:
            continue
        vol = int(tds[1].get_text(strip=True).replace(",","") or 0)
        close = float(tds[2].get_text(strip=True).replace(",","") or 0)
        change_text = tds[3].get_text(strip=True)
        change = 0.0
        # change % is column 4
        if len(tds) >=5:
            pct_text = tds[4].get_text(strip=True).replace("%","").replace("+","")
            try:
                change = float(pct_text)
            except:
                change = 0.0

        if close > 0:
            c.execute("INSERT INTO daily_prices VALUES (?,?,?,?,?)",(ticker,today,close,change,vol))
            count += 1
            print(f"{ticker}: {close} {change}% vol {vol}")
    except Exception as e:
        print(f"Fail {ticker}: {e}")
        continue

conn.commit()
conn.close()
print(f"--- DONE: Scraped {count} REAL tickers for {today} ---")

if count < 5:
    raise Exception(f"Only {count} tickers, site may have changed")
