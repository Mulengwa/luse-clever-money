import sqlite3
from datetime import datetime
from database import get_conn

SAMPLE_DATA = [
    {"date":"2026-09-18", "Symbol":"BATZ", "Closing":0.75, "Change":0.03, "Traded":1000, "BidVol":500, "Bid":0.74, "Ask":0.76, "AskVol":600},
    {"date":"2026-09-18", "Symbol":"LASI", "Closing":25924.31, "Change":0.05, "Traded":0, "BidVol":0, "Bid":0, "Ask":0, "AskVol":0},
    {"date":"2026-10-09", "Symbol":"BATZ", "Closing":12.95, "Change":0.46, "Traded":540, "BidVol":100, "Bid":12.9, "Ask":13.0, "AskVol":200},
    {"date":"2026-10-09", "Symbol":"LASI", "Closing":25669.88, "Change":-28.28, "Traded":0, "BidVol":0, "Bid":0, "Ask":0, "AskVol":0},
]

def parse_closing(rows):
    conn = get_conn()
    cur = conn.cursor()
    for r in rows:
        ticker = r["Symbol"].strip()
        is_index = 1 if ticker == "LASI" else 0
        is_off = 0
        cur.execute("""
        INSERT OR REPLACE INTO prices (date,ticker,close_price,daily_change,traded_vol,bid_vol,bid_price,ask_price,ask_vol,is_index,is_off_market,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (r["date"], ticker, r["Closing"], r["Change"], r["Traded"], r["BidVol"], r["Bid"], r["Ask"], r["AskVol"], is_index, is_off, "NEOS/SBZ"))
        if is_index:
            cur.execute("INSERT OR REPLACE INTO lasi (date,close,change) VALUES (?,?,?)", (r["date"], r["Closing"], r["Change"]))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    parse_closing(SAMPLE_DATA)
    print("Scraped")
