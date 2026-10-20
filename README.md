# luse-clever-money

On-demand LuSE (Lusaka Securities Exchange) market wrap for CleverMoney Zambia.

## Data sources — official only

1. [luse.co.zm/trading/market-data](https://www.luse.co.zm/trading/market-data/) (HTTP or Playwright)
2. Homepage tickers
3. **`data/manual_prices.csv`** when Cloudflare blocks bots (recommended for now)

No third-party aggregators. No fabricated prices.

## Recommended daily flow (Windows / Surface)

Cloudflare often returns **403** to scripts. Use official numbers via CSV:

1. Open the [Market Data](https://www.luse.co.zm/trading/market-data/) page in your browser.
2. Fill `data/manual_prices.csv` (see [docs/MANUAL_PRICES.md](docs/MANUAL_PRICES.md)).
3. Start the runner (`run.cmd`) if using Actions.
4. **Actions → Daily LuSE Wrap → Run workflow** (branch with latest code), **or** run locally:

```cmd
pip install -r requirements.txt
python src\scraper_v2.py
python src\generate_posts.py
python src\social_captions.py
```

## Honest data policy

If fewer than 5 tickers are available from any allowed source, **no prices are stored**.

## Optional Playwright

```cmd
pip install playwright
playwright install chromium
```

## Project structure

```
.github/workflows/   # self-hosted daily/weekly
src/                 # scraper, DB, image, captions
data/                # manual_prices.csv (you create)
docs/
posts/
```

## Attribution

Posts credit the source used. Not affiliated with LuSE.
