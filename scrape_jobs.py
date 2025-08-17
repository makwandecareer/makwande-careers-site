name: Daily Job Scraper

on:
  schedule:
    - cron: "0 4 * * *"   # every day at 04:00 UTC (adjust if you like)
  workflow_dispatch:      # run it manually from the Actions tab
  push:
    paths:
      - "jobs.csv"        # if jobs.csv changes, trigger sync

permissions:
  contents: write

jobs:
  scrape-and-sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install -U pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt || true; fi

      # 👉 your scraper MUST write jobs.csv at repo root (adjust command/path)
      - name: Run scraper
        run: |
          python scraper.py --out jobs.csv

      - name: Commit CSV if changed
        run: |
          if [[ -n "$(git status --porcelain jobs.csv)" ]]; then
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add jobs.csv
            git commit -m "chore: update jobs.csv (auto)"
            git push
          else
            echo "No changes to jobs.csv"
          fi

      - name: Trigger backend sync (GitHub CSV ➜ Snowflake)
        env:
          SYNC_URL: ${{ secrets.BACKEND_SYNC_URL }}      # e.g. https://YOUR-BACKEND/api/sync/github
          SYNC_TOKEN: ${{ secrets.BACKEND_SYNC_TOKEN }}  # must match SYNC_TOKEN in Render
        run: |
          curl -fsSL -X POST "$SYNC_URL" -H "X-Sync-Token: $SYNC_TOKEN"
