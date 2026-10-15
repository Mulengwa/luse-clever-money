import os
import sqlite3
import glob
from datetime import date

print("Generating captions...")

DB = "luse_v2.db"
POST_DIR = "posts"
os.makedirs(POST_DIR, exist_ok=True)

caption = None
try:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "SELECT ticker, change FROM daily_prices WHERE date=? ORDER BY change DESC LIMIT 1",
        (str(date.today()),),
    )
    row = c.fetchone()
    conn.close()

    if row:
        top_ticker, top_change = row
        sign = "+" if top_change >= 0 else ""
        caption = (
            f"🔥 LuSE Daily Wrap {date.today()}\n\n"
            f"Top Mover: {top_ticker} {sign}{top_change:.2f}%\n\n"
            f"Follow @CleverMoneyZM for daily LuSE updates.\n\n"
            f"#LuSE #Zambia #Investing"
        )
    else:
        caption = (
            f"LuSE Daily Wrap {date.today()}\n\n"
            f"No live market data available today.\n"
            f"Follow @CleverMoneyZM for updates when the market is open.\n\n"
            f"#LuSE #Zambia"
        )
except Exception as e:
    print(f"Caption error: {e}")
    caption = (
        f"LuSE Daily Wrap {date.today()}\n\n"
        f"Stay tuned for market updates.\n"
        f"Follow @CleverMoneyZM #LuSE"
    )

pngs = glob.glob(f"{POST_DIR}/*.png")
if pngs:
    latest = sorted(pngs)[-1]
    txt_file = latest.replace(".png", "_caption.txt")
    with open(txt_file, "w") as f:
        f.write(caption)
    print(f"Saved caption {txt_file}")
else:
    print("No PNG found yet for caption")

print("Captions done")
