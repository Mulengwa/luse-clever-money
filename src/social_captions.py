import sqlite3
from database import get_conn
from datetime import datetime
import os

def caption(date_str):
    return f"""📊 LuSE Daily Wrap {date_str} | Clever Money

LASI update + Top Movers inside.

ACCA student journey tracking all 22 LuSE stocks daily from Kitwe.

Source: LuSE / Stockbrokers Zambia / NEOS
Data footer: Data and Chart Provided by: NEOS
#LuSE #Zambia #Copperbelt #CleverMoney #InvestZambia

Educational only, not investment advice. ACCA learning project.
"""

if __name__ == "__main__":
    os.makedirs("posts", exist_ok=True)
    d = "2026-10-09"
    open(f"posts/caption_{d}.txt","w", encoding="utf-8").write(caption(d))
    print("Caption done")
