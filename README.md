# luse-clever-money

Automated daily LuSE (Lusaka Securities Exchange) market wrap for CleverMoney Zambia.

## What it does

- Scrapes live equity prices from [afx.kwayisi.org/luse](https://afx.kwayisi.org/luse/)
- Stores them in a local SQLite database
- Generates a 1080×1080 "Daily Wrap" image + social caption
- Commits the results via GitHub Actions (weekdays)

## Honest data policy

If the scraper cannot reach the data source or returns fewer than 5 tickers, **no prices are stored** for that day. The generated post clearly states that live data is unavailable instead of showing stale or fabricated numbers.

## Project structure

```
.github/workflows/
  daily.yml      # weekday 16:30 CAT
  weekly.yml     # Sunday
src/
  database.py        # schema setup
  scraper_v2.py      # LuSE scraper
  generate_posts.py  # image + caption
  social_captions.py # caption refinement
posts/               # generated images & captions
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

- The SQLite DB (`luse_v2.db`) is git-ignored and recreated as needed.
- Fonts (DejaVu) are installed in the GitHub Actions runner.
- Duplicate workflow files under `src/.github/` are obsolete and can be removed.
