# luse-clever-money

Automated / on-demand LuSE (Lusaka Securities Exchange) market wrap for CleverMoney Zambia.

## Data sources — official only

1. [luse.co.zm/trading/market-data](https://www.luse.co.zm/trading/market-data/)
2. [luse.co.zm](https://www.luse.co.zm/) homepage tickers

No third-party aggregators. No fabricated prices.

## How to run (recommended on Windows / Surface)

Official LuSE is behind Cloudflare, so **GitHub-hosted runners usually fail**. Use one of:

### A. On-demand GitHub Action (self-hosted runner)

1. Register a Windows self-hosted runner (see [docs/SELF_HOSTED.md](docs/SELF_HOSTED.md)).
2. Turn the machine on when you want a wrap.
3. **Actions** → **Daily LuSE Wrap** → **Run workflow**.

You do **not** need the device on 24/7.

### B. Fully local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
```

## Honest data policy

If official sources cannot be reached, **no prices are stored**. The post says live data is unavailable.

## Project structure

```
.github/workflows/   # daily.yml, weekly.yml (self-hosted)
src/                 # scraper, DB, image, captions
scripts/run_local.ps1
docs/SELF_HOSTED.md
posts/
```

## Attribution

Posts credit the official source. Not affiliated with LuSE.
