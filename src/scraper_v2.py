import sqlite3
import requests
from datetime import date
from bs4 import BeautifulSoup

DB = "luse_v2.db"
URL = "https://afx.kwayisi.org/luse/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CleverMoneyBot/1.0)"}
today = str(date.today())

def ensure_schema(conn):
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

def insert_rows(conn, rows):
    """rows: list of (ticker, date, price, change_pct, volume)"""
    c = conn.cursor()
    c.execute("DELETE FROM daily_prices WHERE date=?", (today,))
    if rows:
        c.executemany("INSERT INTO daily_prices VALUES (?,?,?,?,?)", rows)
    conn.commit()
    return len(rows)

def scrape():
    """Fetch live LuSE data. Returns list of tuples or empty list on any failure."""
    try:
        print(f"Fetching {URL}")
        r = requests.get(URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        rows = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if not any("ticker" in h or "price" in h for h in headers):
                continue

            for tr in table.find_all("tr")[1:]:
                tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                if len(tds) < 4:
                    continue
                try:
                    ticker = tds[0].upper().replace("LUSE:", "").strip()
                    if not ticker or not ticker.isalpha() or len(ticker) > 6:
                        continue

                    vol_str = tds[2].replace(",", "").replace("-", "0") or "0"
                    price_str = tds[3].replace(",", "")
                    change_str = (
                        tds[4].replace(",", "").replace("+", "")
                        if len(tds) > 4
                        else "0"
                    )

                    volume = int(float(vol_str)) if vol_str else 0
                    price = float(price_str)
                    abs_change = float(change_str) if change_str else 0.0

                    if price <= 0 or price > 100000:
                        continue

                    prev = price - abs_change
                    pct = round((abs_change / prev * 100) if prev else 0.0, 2)
                    rows.append((ticker, today, price, pct, volume))
                except (ValueError, IndexError):
                    continue

            if rows:
                break

        return rows
    except Exception as e:
        print(f"Scrape failed: {type(e).__name__}: {e}")
        return []

def main():
    conn = sqlite3.connect(DB)
    ensure_schema(conn)

    rows = scrape()

    if len(rows) < 5:
        print(
            f"Only {len(rows)} tickers scraped — NOT inserting any data "
            "(avoids misleading prices)"
        )
        insert_rows(conn, [])  # clear today so downstream knows there is no live data
        print("No live data stored for today")
    else:
        count = insert_rows(conn, rows)
        print(f"Stored {count} live tickers for {today}")

    conn.close()

if __name__ == "__main__":
    main()
