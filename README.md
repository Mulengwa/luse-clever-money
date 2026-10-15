# luse-clever-money

Automated daily LuSE (Lusaka Securities Exchange) market wrap for CleverMoney Zambia.

## What it does

- Scrapes live equity prices from **official LuSE sources** first
- Falls back to a public aggregator only if official pages are unreachable
- Generates a 1080×1080 "Daily Wrap" image + social caption
- Commits results via GitHub Actions (weekdays)

## Data sources (priority order)

1. **Official** – [luse.co.zm/trading/market-data](https://www.luse.co.zm/trading/market-data/)
2. **Official** – [luse.co.zm](https://www.luse.co.zm/) homepage tickers
3. **Unofficial last resort** – [afx.kwayisi.org/luse](https://afx.kwayisi.org/luse/)

Every post attributes the source used.

## Honest data policy

If all sources fail or return fewer than 5 tickers, **no prices are stored** for that day. The generated post clearly states that live data is unavailable — it never shows fabricated or stale numbers as live data.

## Legal / attribution notes

- Closing prices are published by LuSE for public monitoring (see LuSE FAQ).
- This project makes one polite request per weekday, identifies itself with a User-Agent, and produces derived social content with attribution.
- It does **not** resell a raw data feed. For commercial redistribution of market data, contact LuSE for licensing.
- This is not legal advice.

## Project structure

```
.github/workflows/
  daily.yml      # weekday ~16:30 CAT
  weekly.yml     # Sunday
src/
  database.py
  scraper_v2.py
  generate_posts.py
  social_captions.py
posts/
requirements.txt
```

## Running locally

```bash
pip install -r requirements.txt
python src/database.py
python src/scraper_v2.py
python src/generate_posts.py
python src/social_captions.py
```

## Notes

- `luse_v2.db` is git-ignored.
- DejaVu fonts are installed on the GitHub Actions runner.
