from PIL import Image, ImageDraw, ImageFont
import sqlite3, os
from datetime import datetime
from database import get_conn

BRAND_GREEN = "#1ED760"
W, H = 1080, 1080

def get_gainers_losers(df):
    # V2.1 FIX: exclude LASI, exclude 0 volume, exclude null change
    filtered = df[(df["is_index"]==0) & (df["traded_vol"]>0) & (df["daily_change"].notna())]
    gainers = filtered.sort_values("daily_change", ascending=False).head(3)
    losers = filtered.sort_values("daily_change").head(3)
    return gainers, losers

def make_daily(date_str):
    import pandas as pd
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM prices WHERE date=?", conn, params=(date_str,))
    conn.close()
    if df.empty:
        print(f"No data for {date_str}")
        return
    img = Image.new("RGB", (W,H), "black")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,120], fill=BRAND_GREEN)
    # Use default font (no TTF needed on Actions)
    draw.text((40,30), f"Clever Money | LuSE Daily Wrap {date_str}", fill="black")
    lasi_row = df[df["ticker"]=="LASI"]
    lasi_txt = f"LASI {lasi_row.iloc[0]['close_price']} ({lasi_row.iloc[0]['daily_change']})" if not lasi_row.empty else "LASI N/A"
    draw.text((40,150), lasi_txt, fill="white")
    try:
        g,l = get_gainers_losers(df)
        y=220
        draw.text((40,y), f"Top Gainer: {g.iloc[0]['ticker']} {g.iloc[0]['daily_change']}", fill=BRAND_GREEN)
        draw.text((40,y+40), f"Top Loser: {l.iloc[0]['ticker']} {l.iloc[0]['daily_change']}", fill="white")
    except: pass
    draw.text((40, H-60), "Source: LuSE | @CleverMoneyZM | Not investment advice", fill="white")
    os.makedirs("posts", exist_ok=True)
    path = f"posts/Daily_Wrap_{date_str}.png"
    img.save(path)
    print(f"Saved {path}")

if __name__ == "__main__":
    import sys
    date = "2026-10-09"
    if len(sys.argv)>2 and sys.argv[1]=="--weekly":
        date = sys.argv[2]
    make_daily(date)
