import os
import sys
import traceback
import pandas as pd
import snowflake.connector

# ✅ Import your scraping function from scrape_jobs.py
from scrape_jobs import scrape_jobs


def main():
    try:
        print("🚀 Starting job scraper...")

        # ✅ 1. SCRAPE JOBS
        jobs_df = scrape_jobs()  
        print(f"✅ Scraped {len(jobs_df)} jobs")

        # ✅ Ensure DataFrame column names are uppercase to match Snowflake table
        jobs_df.columns = [col.upper() for col in jobs_df.columns]
        print("🔍 DEBUG: DataFrame Columns:", jobs_df.columns.tolist())

        # ✅ 2. CONNECT TO SNOWFLAKE
        print("⛓ Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "AUTOAPPLY_DB"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
        )
        cur = conn.cursor()
        print("✅ Connected to Snowflake")

        # ✅ 3. ENSURE TABLE EXISTS
        cur.execute("""
            CREATE TABLE IF NOT EXISTS MATCHED_JOBS (
                TITLE STRING,
                COMPANY STRING,
                LOCATION STRING,
                COUNTRY STRING,
                INDUSTRY STRING,
                JOB_LEVEL STRING,
                POST_DATE STRING,
                CLOSING_DATE STRING
            )
        """)
        print("✅ MATCHED_JOBS table is ready")

        # ✅ 4. INSERT SCRAPED JOBS INTO SNOWFLAKE
        for _, row in jobs_df.iterrows():
            try:
                cur.execute("""
                    INSERT INTO MATCHED_JOBS (TITLE, COMPANY, LOCATION, COUNTRY, INDUSTRY, JOB_LEVEL, POST_DATE, CLOSING_DATE)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row.get("TITLE"),
                    row.get("COMPANY"),
                    row.get("LOCATION"),
                    row.get("COUNTRY"),
                    row.get("INDUSTRY"),
                    row.get("JOB_LEVEL"),
                    row.get("POST_DATE"),
                    row.get("CLOSING_DATE")
                ))
            except Exception as e:
                print(f"⚠️ Failed to insert row: {row.to_dict()} - Error: {e}")

        conn.commit()
        print("🎉 All jobs successfully loaded into Snowflake!")

    except Exception as e:
        print("❌ ERROR:", e)
        traceback.print_exc()
        sys.exit(1)

    finally:
        try:
            cur.close()
            conn.close()
            print("✅ Snowflake connection closed")
        except:
            pass


if __name__ == "__main__":
    main()














    
















