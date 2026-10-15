"""
LuSE daily price scraper.

Sources (in order):
  1. Official Market Data page  – https://www.luse.co.zm/trading/market-data/
  2. Official homepage tickers  – https://www.luse.co.zm/
  3. Unofficial aggregator      – https://afx.kwayisi.org/luse/  (last resort only)

Policy: never insert fabricated or stale prices. If all sources fail,
store nothing for today so the post generator shows an honest message.
"""

import re
import sqlite3
import requests
from datetime import date
from bs4 import BeautifulSoup

DB = "luse_v2.db"
today = str(date.today())

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CleverMoneyBot/1.0; "
        "+https://github.com/Mulengwa/luse-clever-money)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

OFFICIAL_MARKET_DATA = "https://www.luse.co.zm/trading/market-data/"
OFFICIAL_HOME = "https://www.luse.co.zm/"
UNOFFICIAL_AFX = "https://afx.kwayisi.org/luse/"


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


def _parse_number(text):
    """Parse numbers like '12.49', '-0.46', '1,982', '-', '' → float or None."""
    if text is None:
        return None
    t = str(text).strip().replace(",", "").replace("+", "")
    if not t or t in ("-", "—", "N/A", "n/a"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _pct_from_abs(price, abs_change):
    if price is None or abs_change is None:
        return 0.0
    prev = price - abs_change
    if not prev:
        return 0.0
    return round(abs_change / prev * 100, 2)


def scrape_official_market_data():
    """Parse the official Daily Stock Data table."""
    print(f"Trying official Market Data: {OFFICIAL_MARKET_DATA}")
    r = requests.get(OFFICIAL_MARKET_DATA, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    rows = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        # Need at least Security + Closing Price columns
        if not any("security" in h or "closing" in h for h in headers):
            continue

        # Map column indices
        col = {}
        for i, h in enumerate(headers):
            if "security" in h:
                col["ticker"] = i
            elif "closing" in h or ("price" in h and "bid" not in h and "ask" not in h):
                col["price"] = i
            elif "price change" in h or h == "change":
                col["change"] = i
            elif "volume" in h and "value" not in h:
                col["volume"] = i

        if "ticker" not in col or "price" not in col:
            continue

        for tr in table.find_all("tr")[1:]:
            tds = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(tds) <= max(col.values()):
                continue
            try:
                ticker = tds[col["ticker"]].upper().strip()
                # Skip bond / empty rows
                if not ticker or not re.match(r"^[A-Z]{2,6}$", ticker):
                    continue
                # Normalise known aliases
                if ticker in ("ZCCM-IH", "ZCCM IH"):
                    ticker = "ZCCM"
                if ticker == "ZAMBIA RE":
                    ticker = "ZMRE"
                if ticker == "REIZUSD":
                    ticker = "REIZ"

                price = _parse_number(tds[col["price"]])
                if price is None or price <= 0 or price > 100000:
                    continue

                abs_change = 0.0
                if "change" in col:
                    v = _parse_number(tds[col["change"]])
                    if v is not None:
                        abs_change = v

                volume = 0
                if "volume" in col:
                    v = _parse_number(tds[col["volume"]])
                    if v is not None:
                        volume = int(v)

                pct = _pct_from_abs(price, abs_change)
                rows.append((ticker, today, price, pct, volume))
            except (ValueError, IndexError):
                continue

        if rows:
            break

    print(f"  Official market-data → {len(rows)} tickers")
    return rows


def scrape_official_homepage():
    """Parse homepage price widgets (ticker / price / change blocks)."""
    print(f"Trying official homepage: {OFFICIAL_HOME}")
    r = requests.get(OFFICIAL_HOME, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    # Pattern: TICKER then number then optional +/‑ change on nearby lines
    # Homepage structure from observation: ## AECI \n ## 115.00 \n ## 0.00
    rows = []
    # Find sequences of ALL-CAPS ticker followed by two numbers
    pattern = re.compile(
        r"\b([A-Z]{2,8}(?:-IH)?)\b\s*[\n\r]+\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s*[\n\r]+\s*"
        r"([+\-]?[0-9]+(?:\.[0-9]+)?)",
        re.MULTILINE,
    )
    seen = set()
    for m in pattern.finditer(text):
        ticker = m.group(1).upper()
        if ticker in seen:
            continue
        if ticker in ("LASI", "TRADE", "SENS", "LUSE", "ZMW"):
            continue
        if ticker == "ZCCM-IH":
            ticker = "ZCCM"
        if ticker == "ZAMBIA":
            continue  # part of "ZAMBIA RE"
        price = float(m.group(2))
        abs_change = float(m.group(3))
        if price <= 0 or price > 100000:
            continue
        pct = _pct_from_abs(price, abs_change)
        rows.append((ticker, today, price, pct, 0))
        seen.add(ticker)

    print(f"  Official homepage → {len(rows)} tickers")
    return rows


def scrape_afx():
    """Unofficial last-resort source."""
    print(f"Trying unofficial AFX: {UNOFFICIAL_AFX}")
    r = requests.get(UNOFFICIAL_AFX, headers=HEADERS, timeout=15)
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
                if not ticker or not re.match(r"^[A-Z]{2,6}$", ticker):
                    continue
                vol = _parse_number(tds[2]) or 0
                price = _parse_number(tds[3])
                abs_change = _parse_number(tds[4]) if len(tds) > 4 else 0.0
                if price is None or price <= 0 or price > 100000:
                    continue
                pct = _pct_from_abs(price, abs_change or 0.0)
                rows.append((ticker, today, price, pct, int(vol)))
            except (ValueError, IndexError):
                continue
        if rows:
            break

    print(f"  AFX → {len(rows)} tickers")
    return rows


def scrape():
    """Try sources in order. Return (rows, source_name)."""
    sources = [
        ("LuSE Market Data", scrape_official_market_data),
        ("LuSE Homepage", scrape_official_homepage),
        ("AFX (unofficial)", scrape_afx),
    ]
    for name, fn in sources:
        try:
            rows = fn()
            if len(rows) >= 5:
                return rows, name
            print(f"  {name}: only {len(rows)} tickers — trying next source")
        except Exception as e:
            print(f"  {name} failed: {type(e).__name__}: {e}")
    return [], None


def main():
    conn = sqlite3.connect(DB)
    ensure_schema(conn)

    rows, source = scrape()

    if len(rows) < 5:
        print(
            f"Only {len(rows)} tickers from all sources — "
            "NOT inserting any data (avoids misleading prices)"
        )
        insert_rows(conn, [])
        print("No live data stored for today")
        # Write a small marker so captions know the outcome
        with open("posts/.last_scrape_source", "w") as f:
            f.write("none\n")
    else:
        count = insert_rows(conn, rows)
        print(f"Stored {count} live tickers for {today} (source: {source})")
        with open("posts/.last_scrape_source", "w") as f:
            f.write(f"{source}\n")

    conn.close()


if __name__ == "__main__":
    main()
