import snowflake.connector
import pandas as pd

# --- 1️⃣ CONNECT TO SNOWFLAKE ---
conn = snowflake.connector.connect(
    user="MAKWANDECAREERS",
    password="Makwande@202530",
    account="hpfcrwb-oh67940",
    warehouse="COMPUTE_WH",
    database="AUTOAPPLY_DB",
    schema="PUBLIC"
)

cursor = conn.cursor()

print("✅ Connected to Snowflake")

# --- 2️⃣ READ SCRAPED JOBS CSV ---
csv_file = "top_matched_jobs.csv"   # Change this if your file name changes
df = pd.read_csv(csv_file)

print(f"📄 Loaded {len(df)} jobs from {csv_file}")

# --- 3️⃣ LOOP AND INSERT JOBS INTO SNOWFLAKE ---
insert_query = """
    INSERT INTO MATCHED_JOBS (TITLE, COMPANY, LOCATION, COUNTRY, INDUSTRY, JOB_LEVEL, POST_DATE, CLOSING_DATE)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for _, row in df.iterrows():
    cursor.execute(insert_query, (
        row.get('TITLE', None),
        row.get('COMPANY', None),
        row.get('LOCATION', None),
        row.get('COUNTRY', 'South Africa'),   # Default to South Africa
        row.get('INDUSTRY', 'General'),       # Default if missing
        row.get('JOB_LEVEL', 'Entry Level'),  # Default if missing
        row.get('POST_DATE', None),
        row.get('CLOSING_DATE', None)
    ))

print(f"✅ Inserted {len(df)} jobs into Snowflake")

# --- 4️⃣ COMMIT AND CLOSE CONNECTION ---
conn.commit()
cursor.close()
conn.close()

print("🎉 All scraped jobs uploaded to Snowflake successfully!")
