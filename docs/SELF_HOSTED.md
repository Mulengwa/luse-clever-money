# Self-hosted runner (Windows / Surface Pro)

## Why self-hosted?

`luse.co.zm` is behind Cloudflare. GitHub-hosted runners (datacenter IPs) almost always get a challenge page and never see market data. A runner on your home network is much more likely to reach official sources.

## You do **not** need the machine on 24/7

Recommended for a Surface Pro 3:

1. Turn the device on when you want a wrap.
2. Ensure the runner is running (or start the service).
3. GitHub → **Actions** → **Daily LuSE Wrap** → **Run workflow**.
4. Shut down or sleep when finished.

Missed schedule runs are fine. The scraper never invents prices.

## One-time setup (Windows 10)

1. Install [Git for Windows](https://git-scm.com/download/win) and [Python 3.10+](https://www.python.org/downloads/) (tick **Add to PATH**).
2. Confirm https://www.luse.co.zm/trading/market-data/ loads in your browser.
3. Repo → **Settings** → **Actions** → **Runners** → **New self-hosted runner** → **Windows**.
4. Run the PowerShell commands GitHub shows (`config.cmd` with the token).
5. Install as a service (elevated PowerShell):
   ```powershell
   .\svc.cmd install
   .\svc.cmd start
   ```
6. Workflows already use `runs-on: self-hosted`.

## Fully local (no Actions)

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
```

Then commit `posts\` yourself if you want it on GitHub.

## Safety notes

- Workflows execute code on **your** machine. Only trust collaborators who can push.
- Prefer approving workflows from forks; keep the runner repo-scoped.
- Do not leave banking sessions on the same Windows account that runs the service if you can avoid it.

## Optional schedule

`daily.yml` still has a weekday cron. It only runs if the Surface is on and the runner is online at that time. Otherwise use **Run workflow**.
