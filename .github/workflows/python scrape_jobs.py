name: Daily Job Scraper

on:
  schedule:
    # Runs every day at 06:00 SADC time (UTC+2)
    - cron: '0 4 * * *'   # 04:00 UTC = 06:00 SADC
  workflow_dispatch:       # allows manual trigger from GitHub UI

jobs:
  run-scraper:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install Chrome for Selenium
        run: |
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable
          sudo apt-get install -y chromium-chromedriver
          export PATH=$PATH:/usr/lib/chromium-browser/

      - name: Run scraper and load to Snowflake
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ROLE: ACCOUNTADMIN
          SNOWFLAKE_WAREHOUSE: COMPUTE_WH
          SNOWFLAKE_DATABASE: AUTOAPPLY_DB
          SNOWFLAKE_SCHEMA: PUBLIC
        run: |
          python main.py


