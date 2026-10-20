# Manual prices (recommended while Cloudflare blocks bots)

Python HTTP clients currently get **HTTP 403** from `luse.co.zm`. Your browser still works.

## Daily steps

1. Open https://www.luse.co.zm/trading/market-data/ in Chrome.
2. Copy closes into `data/manual_prices.csv` (create from the example).

```text
copy data\manual_prices.example.csv data\manual_prices.csv
```

3. Edit with Notepad. Format:

```csv
ticker,price,change,volume
ZCCM,25.00,1.25,1200
ZSUG,35.50,-0.50,800
...
```

- `change` = **percent** change (as on the site or calculated).
- `volume` optional (use `0` if unknown).
- At least **5** rows required.

4. Run the workflow (**Daily LuSE Wrap**) or locally:

```cmd
python src\scraper_v2.py
python src\generate_posts.py
```

The scraper tries live HTTP → Playwright (if installed) → **this CSV**.

## Optional: Playwright (auto browser)

```cmd
pip install playwright
playwright install chromium
```

Then a normal scrape may work without the CSV. On a Surface Pro 3 this is heavier; CSV is lighter.
