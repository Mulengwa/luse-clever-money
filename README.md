# luse-clever-money

Automated daily LuSE (Lusaka Securities Exchange) market wrap for CleverMoney Zambia.

## Data sources — official only

1. [luse.co.zm/trading/market-data](https://www.luse.co.zm/trading/market-data/)
2. [luse.co.zm](https://www.luse.co.zm/) homepage tickers

No third-party aggregators. No fabricated prices.

## Cloudflare limitation

`luse.co.zm` sits behind **Cloudflare managed challenge**.  
Plain HTTP clients (and most GitHub-hosted runners) receive **403 / “Just a moment…”** and never see the price table.

### Recommended setup for reliable official data

Use a **self-hosted GitHub Actions runner** on a machine that can open the LuSE site in a normal browser (e.g. PC or small VPS in Zambia):

1. Repo → Settings → Actions → Runners → New self-hosted runner
2. Install the runner on your machine and start it
3. In `.github/workflows/daily.yml` set:

```yaml
runs-on: self-hosted
```

Then the scraper runs from an IP Cloudflare is more likely to allow.

Optional long-term: email LuSE (`customerservice@luse.co.zm`) and ask for a data feed / API for a non-commercial market-education project.

## Honest data policy

If official sources cannot be reached, **no prices are stored**. The post says live data is unavailable.

## Running locally (best for testing official access)

```bash
pip install -r requirements.txt
python src/database.py
python src/scraper_v2.py
python src/generate_posts.py
python src/social_captions.py
```

If your local network can open luse.co.zm in Chrome, the scraper should succeed.

## Attribution

Posts credit the official source used. Not affiliated with LuSE.
