name: run-scraper

on:
  schedule:
    - cron: "0 4 * * *"        # daily 04:00 UTC
  workflow_dispatch:           # allow manual run

permissions:
  contents: write

jobs:
  scrape-and-sync:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install -U pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      # If you use Selenium, keep your Chrome step; otherwise remove it.
      # - name: Install Chrome for Selenium
      #   uses: browser-actions/setup-chrome@v1

      # 👇 Run YOUR scraper script — adjust this command to your real entrypoint
      - name: Run scraper -> jobs.csv
        run: |
          python scraper.py --out jobs.csv

      # Show a bit of output for debugging
      - name: Show head and count
        run: |
          head -n 20 jobs.csv || true
          wc -l jobs.csv || true

      # Commit only if changed
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

      # Trigger your backend to ingest the RAW CSV from GitHub -> Snowflake
      - name: Trigger backend sync
        env:
          SYNC_URL: https://autoapply-api.onrender.com/api/sync/github
          SYNC_TOKEN: ${{ secrets.BACKEND_SYNC_TOKEN }}
        run: |
          # Try POST, fall back to GET with ?token=
          curl -fsSL -X POST "$SYNC_URL" -H "X-Sync-Token: $SYNC_TOKEN" \
          || curl -fsSL "$SYNC_URL?token=$SYNC_TOKEN"

      # Attach the produced CSV so you can download and verify the rows
      - name: Upload CSV artifact
        uses: actions/upload-artifact@v4
        with:
          name: jobs.csv
          path: jobs.csv
          if-no-files-found: error

