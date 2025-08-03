from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import snowflake.connector
import os

app = FastAPI()

# ✅ Snowflake connection details (you already have these)
SNOWFLAKE_ACCOUNT = "hpfcrwb-oh67940"
SNOWFLAKE_USER = "MAKWANDECAREERS"
SNOWFLAKE_PASSWORD = "Makwande@202530"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "AUTOAPPLY_DB"
SNOWFLAKE_SCHEMA = "PUBLIC"

# ✅ Job model for FastAPI
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    post_date: str
    closing_date: str

# ✅ Connect to Snowflake function
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

@app.get("/jobs", response_model=List[Job])
def get_jobs():
    try:
        conn = get_snowflake_connection()
        cur = conn.cursor()
        # ✅ Change columns to match your MATCHED_JOBS table
        cur.execute("""
            SELECT ID, TITLE, COMPANY, LOCATION, POST_ADVERTISED_DATE, CLOSING_DATE 
            FROM MATCHED_JOBS
            LIMIT 20
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # ✅ Convert query results into JSON for FastAPI
        jobs = []
        for row in rows:
            jobs.append({
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3],
                "post_date": str(row[4]),
                "closing_date": str(row[5])
            })
        return jobs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {e}")



    
















