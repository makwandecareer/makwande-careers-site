import os
import snowflake.connector
from fastapi import FastAPI

app = FastAPI()

# ✅ Connect to Snowflake function
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

# ✅ Fetch jobs from Snowflake
@app.get("/jobs")
def get_jobs(country: str = None, limit: int = 50, page: int = 1):
    conn = get_snowflake_connection()
    cur = conn.cursor()

    offset = (page - 1) * limit

    query = "SELECT TITLE, COMPANY, LOCATION, COUNTRY, INDUSTRY, JOB_LEVEL, POST_DATE, CLOSING_DATE FROM MATCHED_JOBS"
    params = []

    if country:
        query += " WHERE COUNTRY = %s"
        params.append(country)

    query += " ORDER BY POST_DATE DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {"jobs": [
        {
            "title": row[0],
            "company": row[1],
            "location": row[2],
            "country": row[3],
            "industry": row[4],
            "job_level": row[5],
            "post_date": row[6],
            "closing_date": row[7]
        } for row in rows
    ]}















    
















