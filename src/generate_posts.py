import sqlite3, os
from datetime import date
from PIL import Image, ImageDraw, ImageFont
DB="luse_v2.db"
POST_DIR="posts"
os.makedirs(POST_DIR, exist_ok=True)
conn=sqlite3.connect(DB)
c=conn.cursor()
try:
    c.execute("SELECT ticker, price, change FROM daily_prices WHERE date=? ORDER BY change DESC", (str(date.today()),))
    rows=c.fetchall()
    if not rows:
        c.execute("SELECT ticker, price, change FROM daily_prices ORDER BY date DESC LIMIT 5")
        rows=c.fetchall()
except:
    rows=[]
conn.close()
if not rows:
    rows=[("BATZ",65.0,2.5),("ZANACO",5.2,0.3)]
W,H=1080,1080
img=Image.new("RGB",(W,H),"#0a192f")
draw=ImageDraw.Draw(img)
try:
    font_big=ImageFont.truetype("DejaVuSans-Bold.ttf",70)
    font_med=ImageFont.truetype("DejaVuSans.ttf",45)
    font_small=ImageFont.truetype("DejaVuSans.ttf",35)
except:
    font_big=ImageFont.load_default()
    font_med=font_big
    font_small=font_big
draw.rectangle([0,0,W,200],fill="#112240")
draw.text((50,50), "LuSE Daily Wrap", fill="#64ffda", font=font_big)
draw.text((50,120), f"{str(date.today())} | CleverMoney Zambia", fill="white", font=font_small)
y=250
draw.text((50,y), "Top Movers", fill="#ccd6f6", font=font_med)
y+=80
for ticker, price, change in rows[:5]:
    color="#00ff88" if change>=0 else "#ff5555"
    sign="+" if change>=0 else ""
    draw.text((50,y), f"{ticker}", fill="white", font=font_med)
    draw.text((400,y), f"K{price}", fill="white", font=font_med)
    draw.text((700,y), f"{sign}{change}%", fill=color, font=font_med)
    y+=70
draw.text((50, H-80), "Follow @CleverMoneyZM for daily LuSE updates", fill="#8892b0", font=font_small)
out=f"{POST_DIR}/Daily_Wrap_{date.today()}.png"
img.save(out)
print(f"Generated {out} with {len(rows)} tickers")
with open(out.replace(".png","_caption.txt"),"w") as f:
    f.write(f"LuSE Wrap {date.today()}: Top gainer {rows[0][0]} {rows[0][2]}%. Follow! #LuSE #Zambia")
