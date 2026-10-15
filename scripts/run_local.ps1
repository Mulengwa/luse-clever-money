# Local LuSE wrap on Windows (no GitHub Actions required).
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
# From the repo root, with Python 3.10+ on PATH.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "Installing deps (if needed)..."
pip install -r requirements.txt -q

Write-Host "Preparing database..."
python src/database.py

Write-Host "Scraping official LuSE sources..."
python src/scraper_v2.py

Write-Host "Generating image..."
python src/generate_posts.py

Write-Host "Generating caption..."
python src/social_captions.py

Write-Host "Done. Check the posts\ folder."
Write-Host "Optional: git add posts; git commit; git push"
