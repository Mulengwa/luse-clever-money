import sqlite3
import os
from datetime import date
from PIL import Image, ImageDraw, ImageFont

DB = "luse_v2.db"
POST_DIR = "posts"
os.makedirs(POST_DIR, exist_ok=True)

def get_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf",
        "DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

conn = sqlite3.connect(DB)
c = conn.cursor()
rows = []
try:
    c.execute(
        "SELECT ticker, price, change FROM daily_prices WHERE date=? ORDER BY change DESC",
        (str(date.today()),),
    )
    rows = c.fetchall()
except Exception as e:
    print(f"DB query failed: {e}")
conn.close()

W, H = 1080, 1080
img = Image.new("RGB", (W, H), "#0a192f")
draw = ImageDraw.Draw(img)

font_big = get_font(70)
font_med = get_font(45)
font_small = get_font(35)

draw.rectangle([0, 0, W, 200], fill="#112240")
draw.text((50, 50), "LuSE Daily Wrap", fill="#64ffda", font=font_big)
draw.text(
    (50, 120),
    f"{date.today()} | CleverMoney Zambia",
    fill="white",
    font=font_small,
)

if not rows:
    # Honest message when there is no live data
    draw.text((50, 350), "No live market data", fill="#ff5555", font=font_med)
    draw.text(
        (50, 430),
        "Available for today.",
        fill="#ccd6f6",
        font=font_med,
    )
    draw.text(
        (50, 530),
        "Scrape failed or market closed.",
        fill="#8892b0",
        font=font_small,
    )
    caption = (
        f"LuSE Daily Wrap {date.today()}\n\n"
        "No live market data available today.\n"
        "Follow @CleverMoneyZM for updates when the market is open.\n\n"
        "#LuSE #Zambia"
    )
else:
    y = 250
    draw.text((50, y), "Top Movers", fill="#ccd6f6", font=font_med)
    y += 80

    for ticker, price, change in rows[:5]:
        color = "#00ff88" if change >= 0 else "#ff5555"
        sign = "+" if change >= 0 else ""
        draw.text((50, y), f"{ticker}", fill="white", font=font_med)
        draw.text((350, y), f"K{price:.2f}", fill="white", font=font_med)
        draw.text((700, y), f"{sign}{change:.2f}%", fill=color, font=font_med)
        y += 70

    top = rows[0]
    sign = "+" if top[2] >= 0 else ""
    caption = (
        f"LuSE Wrap {date.today()}: Top mover {top[0]} "
        f"{sign}{top[2]:.2f}%. Follow! #LuSE #Zambia"
    )

draw.text(
    (50, H - 80),
    "Follow @CleverMoneyZM for daily LuSE updates",
    fill="#8892b0",
    font=font_small,
)

out = f"{POST_DIR}/Daily_Wrap_{date.today()}.png"
img.save(out)
print(f"Generated {out} with {len(rows)} tickers")

with open(out.replace(".png", "_caption.txt"), "w") as f:
    f.write(caption)
