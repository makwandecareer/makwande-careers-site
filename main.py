from fastapi import FastAPI
import snowflake.connector
from pydantic import BaseModel
import os

app = FastAPI()

# ✅ Snowflake connection details
SNOWFLAKE_ACCOUNT = "hpfcrwb-oh67940"
SNOWFLAKE_USER = "MAKWANDECAREERS"
SNOWFLAKE_PASSWORD = "Makwande@202530"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "AUTOAPPLY_DB"
SNOWFLAKE_SCHEMA = "PUBLIC"

# ✅ Job Model for FastAPI
class Job(BaseModel):
    job_title: str
    company: str
    location: str
    post_date: str
    closing_date: str

@app.get("/")
def read_root():
    return {"message": "✅ AutoApply API is running and connected to Snowflake"}

@app.get("/jobs")
def get_jobs():
    try:
        # ✅ Connect to Snowflake
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )

        cur = conn.cursor()

        # ✅ Only select existing Snowflake columns
        cur.execute("""
            SELECT JOB_TITLE, COMPANY, LOCATION, POST_DATE, CLOSING_DATE 
            FROM MATCHED_JOBS
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        # ✅ Return jobs in JSON format
        jobs = []
        for row in rows:
            jobs.append({
                "job_title": row[0],
                "company": row[1],
                "location": row[2],
                "post_date": str(row[3]),
                "closing_date": str(row[4])
            })
        return jobs

    except Exception as e:
        return {"error": str(e)}






    
















