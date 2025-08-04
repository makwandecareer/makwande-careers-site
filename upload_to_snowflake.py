import pandas as pd
import snowflake.connector

print("✅ Starting Snowflake manual upload...")

# Load the CSV
try:
    df = pd.read_csv("top_matched_jobs.csv")
    print(f"📄 Loaded {len(df)} rows from CSV")
except Exception as e:
    print("❌ Failed to read CSV:", e)
    exit()

# Connect to Snowflake
try:
    conn = snowflake.connector.connect(
        user='MAKWANDECAREERS',
        password='Makwande@202530',
        account='hpfcrwb-oh67940',
        warehouse='COMPUTE_WH',
        database='AUTOAPPLY_DB',
        schema='PUBLIC',
        role='ACCOUNTADMIN'
    )
    print("🔌 Connected to Snowflake")
except Exception as e:
    print("❌ Connection failed:", e)
    exit()

# Create table if it doesn't exist
try:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MATCHED_JOBS (
            job_title STRING,
            company STRING,
            location STRING,
            job_url STRING,
            match_score FLOAT,
            description STRING
        )
    """)
    print("📦 Table MATCHED_JOBS is ready")
except Exception as e:
    print("❌ Failed to create table:", e)
    conn.close()
    exit()

# Insert each row (no S3, no staging)
insert_sql = """
    INSERT INTO MATCHED_JOBS (job_title, company, location, job_url, match_score, description)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

rows_inserted = 0
try:
    for _, row in df.iterrows():
        cursor.execute(insert_sql, (
            row.get("job_title", ""),
            row.get("company", ""),
            row.get("location", ""),
            row.get("job_url", ""),
            float(row.get("match_score", 0)),
            row.get("description", "")
        ))
        rows_inserted += 1
    conn.commit()
    print(f"✅ Inserted {rows_inserted} rows into Snowflake (NO S3 used)")
except Exception as e:
    print("❌ Failed to insert data:", e)
finally:
    cursor.close()
    conn.close()
    print("🔒 Snowflake connection closed")





