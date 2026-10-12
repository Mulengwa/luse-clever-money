import os, sqlite3
from datetime import date
print("Generating captions...")

DB="luse_v2.db"
POST_DIR="posts"
os.makedirs(POST_DIR, exist_ok=True)

# Simple caption generation without get_conn
try:
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("SELECT ticker, change FROM daily_prices WHERE date=? ORDER BY change DESC LIMIT 1", (str(date.today()),))
    row=c.fetchone()
    conn.close()
    if row:
        top_ticker, top_change = row
        caption = f"🔥 LuSE Daily Wrap {date.today()}\n\nTop Mover: {top_ticker} +{top_change}%\n\nBATZ still leading market! Follow @CleverMoneyZM for daily LuSE updates.\n\n#LuSE #Zambia #Investing"
    else:
        caption = f"LuSE Daily Wrap {date.today()} - Market update! Follow @CleverMoneyZM #LuSE"
except Exception as e:
    print(f"Caption fallback: {e}")
    caption = f"LuSE Daily Wrap {date.today()} - Stay tuned! #LuSE"

# Find latest PNG and create caption file
import glob
pngs=glob.glob(f"{POST_DIR}/*.png")
if pngs:
    latest=sorted(pngs)[-1]
    txt_file=latest.replace(".png","_caption.txt")
    with open(txt_file,"w") as f:
        f.write(caption)
    print(f"Saved caption {txt_file}")
else:
    print("No PNG found yet for caption")

print("Captions done")
