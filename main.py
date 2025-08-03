from scrape_jobs import scrape_jobs
import os
import sys
import traceback
import snowflake.connector
import pandas as pd

def main():
    try:
        print("🚀 Starting job scraper...")

        # ✅ 1. SCRAPE JOBS
        jobs_df = scrape_jobs()
        print(f"✅ Scraped {len(jobs_df)} jobs")

        # ✅ 2. CONNECT TO SNOWFLAKE
        print("🔗 Connecting to Snowflake...")
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
                POST_DATE DATE,
                CLOSING_DATE DATE
            )
        """)
        print("✅ Ensured MATCHED_JOBS table exists")

        # ✅ 4. CLEAR OLD DATA (optional, remove if you want to append instead of overwrite)
        cur.execute("TRUNCATE TABLE MATCHED_JOBS")
        print("✅ Old data cleared")

        # ✅ 5. UPLOAD NEW JOBS
        print("⬆️ Uploading jobs to Snowflake...")
        for _, row in jobs_df.iterrows():
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

        conn.commit()
        print(f"✅ Successfully uploaded {len(jobs_df)} jobs to Snowflake")

    except Exception as e:
        print("❌ ERROR during execution")
        traceback.print_exc()
        sys.exit(1)

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    main()













    
















