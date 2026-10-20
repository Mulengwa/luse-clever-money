"""
LuSE daily price scraper — OFFICIAL SOURCES ONLY.

Order of attempts:
  1. HTTP (cloudscraper/requests) to official LuSE pages
  2. Playwright browser (optional) if installed — beats many Cloudflare challenges
  3. data/manual_prices.csv — recommended when HTTP is blocked

No third-party aggregators. No fabricated prices.
"""

import csv
import os
import re
import sqlite3
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

DB = "luse_v2.db"
today = str(date.today())
MANUAL_CSV = Path("data/manual_prices.csv")

OFFICIAL_MARKET_DATA = "https://www.luse.co.zm/trading/market-data/"
OFFICIAL_HOME = "https://www.luse.co.zm/"


def _session():
    try:
        import cloudscraper

        return cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    except Exception:
        import requests

        s = requests.Session()
        s.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        return s


def ensure_schema(conn):
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_prices (
            ticker TEXT,
            date   TEXT,
            price  REAL,
            change REAL,
            volume INTEGER
        )
        """
    )
    conn.commit()


def insert_rows(conn, rows):
    c = conn.cursor()
    c.execute("DELETE FROM daily_prices WHERE date=?", (today,))
    if rows:
        c.executemany("INSERT INTO daily_prices VALUES (?,?,?,?,?)", rows)
    conn.commit()
    return len(rows)


def _parse_number(text):
    if text is None:
        return None
    t = str(text).strip().replace(",", "").replace("%", "").replace("+", "")
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


def _normalize_ticker(raw):
    t = raw.upper().strip()
    aliases = {
        "ZCCM-IH": "ZCCM",
        "ZCCM IH": "ZCCM",
        "ZAMBIA RE": "ZMRE",
        "REIZUSD": "REIZ",
    }
    return aliases.get(t, t)


def _parse_tables_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if not any("security" in h or "closing" in h for h in headers):
            continue

        col = {}
        for i, h in enumerate(headers):
            if "security" in h:
                col["ticker"] = i
            elif "closing" in h or (
                "price" in h and "bid" not in h and "ask" not in h and "change" not in h
            ):
                col["price"] = i
            elif "price change" in h or h.strip() == "change":
                col["change"] = i
            elif "%" in h and "change" in h:
                col["pct"] = i
            elif "volume" in h and "value" not in h:
                col["volume"] = i

        if "ticker" not in col or "price" not in col:
            continue

        for tr in table.find_all("tr")[1:]:
            tds = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(tds) <= max(col.values()):
                continue
            try:
                ticker = _normalize_ticker(tds[col["ticker"]])
                if not re.match(r"^[A-Z]{2,6}$", ticker):
                    continue
                price = _parse_number(tds[col["price"]])
                if price is None or price <= 0 or price > 100000:
                    continue
                pct = 0.0
                if "pct" in col:
                    v = _parse_number(tds[col["pct"]])
                    if v is not None:
                        pct = v
                elif "change" in col:
                    abs_change = _parse_number(tds[col["change"]])
                    pct = _pct_from_abs(price, abs_change)
                volume = 0
                if "volume" in col:
                    v = _parse_number(tds[col["volume"]])
                    if v is not None:
                        volume = int(v)
                rows.append((ticker, today, price, pct, volume))
            except (ValueError, IndexError):
                continue
        if rows:
            break
    return rows


def scrape_official_market_data(session):
    print(f"Trying official Market Data: {OFFICIAL_MARKET_DATA}")
    r = session.get(OFFICIAL_MARKET_DATA, timeout=45)
    print(f"  HTTP {r.status_code}, body length {len(r.text)}")
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} (likely Cloudflare challenge)")
    if "Just a moment" in r.text or "cf-mitigated" in r.text.lower():
        raise RuntimeError("Cloudflare challenge page returned")
    rows = _parse_tables_from_html(r.text)
    print(f"  Official market-data → {len(rows)} tickers")
    return rows


def scrape_official_homepage(session):
    print(f"Trying official homepage: {OFFICIAL_HOME}")
    r = session.get(OFFICIAL_HOME, timeout=45)
    print(f"  HTTP {r.status_code}, body length {len(r.text)}")
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} (likely Cloudflare challenge)")
    if "Just a moment" in r.text or "cf-mitigated" in r.text.lower():
        raise RuntimeError("Cloudflare challenge page returned")

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)
    rows = []
    pattern = re.compile(
        r"\b([A-Z]{2,8}(?:-IH)?)\b\s*[\n\r]+\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s*[\n\r]+\s*"
        r"([+\-]?[0-9]+(?:\.[0-9]+)?)",
        re.MULTILINE,
    )
    seen = set()
    skip = {"LASI", "TRADE", "SENS", "LUSE", "ZMW", "ZAMBIA"}
    for m in pattern.finditer(text):
        ticker = _normalize_ticker(m.group(1))
        if ticker in seen or ticker in skip:
            continue
        if not re.match(r"^[A-Z]{2,6}$", ticker):
            continue
        price = float(m.group(2))
        abs_change = float(m.group(3))
        if price <= 0 or price > 100000:
            continue
        pct = _pct_from_abs(price, abs_change)
        rows.append((ticker, today, price, pct, 0))
        seen.add(ticker)

    print(f"  Official homepage → {len(rows)} tickers")
    return rows


def scrape_with_playwright():
    """Optional: real browser. pip install playwright && playwright install chromium"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed — skip (pip install playwright)")
        return []

    print(f"Trying Playwright browser: {OFFICIAL_MARKET_DATA}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            page.goto(OFFICIAL_MARKET_DATA, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
    except Exception as e:
        print(f"  Playwright failed: {type(e).__name__}: {e}")
        return []

    if "Just a moment" in html and "Security" in html:
        print("  Playwright still got Cloudflare interstitial")
        return []

    rows = _parse_tables_from_html(html)
    print(f"  Playwright market-data → {len(rows)} tickers")
    return rows


def load_manual_csv():
    """
    data/manual_prices.csv columns (header required):
      ticker,price,change,volume
    - change = percent change (e.g. -0.16 or 1.25)
    - volume optional (default 0)
    Only used when live sources fail or return < 5 rows.
    """
    if not MANUAL_CSV.is_file():
        print(f"  No manual file at {MANUAL_CSV}")
        return []

    print(f"Loading manual prices: {MANUAL_CSV}")
    rows = []
    with MANUAL_CSV.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("  Empty CSV")
            return []
        fields = {h.strip().lower(): h for h in reader.fieldnames if h}
        if "ticker" not in fields or "price" not in fields:
            print("  CSV needs columns: ticker,price,change[,volume]")
            return []
        for line in reader:
            try:
                ticker = _normalize_ticker(line[fields["ticker"]])
                if not re.match(r"^[A-Z]{2,6}$", ticker):
                    continue
                price = _parse_number(line[fields["price"]])
                if price is None or price <= 0:
                    continue
                pct = 0.0
                if "change" in fields:
                    v = _parse_number(line[fields["change"]])
                    if v is not None:
                        pct = v
                volume = 0
                if "volume" in fields:
                    v = _parse_number(line[fields["volume"]])
                    if v is not None:
                        volume = int(v)
                rows.append((ticker, today, price, pct, volume))
            except (KeyError, ValueError):
                continue

    print(f"  Manual CSV → {len(rows)} tickers")
    return rows


def scrape():
    session = _session()

    # 1) Lightweight HTTP
    for name, fn in [
        ("LuSE Market Data", lambda: scrape_official_market_data(session)),
        ("LuSE Homepage", lambda: scrape_official_homepage(session)),
    ]:
        try:
            rows = fn()
            if len(rows) >= 5:
                return rows, name
            print(f"  {name}: only {len(rows)} tickers — trying next")
        except Exception as e:
            print(f"  {name} failed: {type(e).__name__}: {e}")

    # 2) Optional browser
    try:
        rows = scrape_with_playwright()
        if len(rows) >= 5:
            return rows, "LuSE Market Data (Playwright)"
    except Exception as e:
        print(f"  Playwright path failed: {type(e).__name__}: {e}")

    # 3) Manual CSV (your main path while Cloudflare blocks bots)
    rows = load_manual_csv()
    if len(rows) >= 5:
        return rows, "Manual CSV (official figures entered by operator)"

    return [], None


def main():
    os.makedirs("posts", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB)
    ensure_schema(conn)

    rows, source = scrape()

    if len(rows) < 5:
        print(
            f"Only {len(rows)} tickers — NOT inserting any data (avoids misleading prices)."
        )
        print(
            "TIP: Copy data/manual_prices.example.csv → data/manual_prices.csv "
            "and fill today's official LuSE closes, then re-run."
        )
        insert_rows(conn, [])
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
