from fastapi import FastAPI, HTTPException
from typing import List, Optional
import snowflake.connector
from pydantic import BaseModel
import os

app = FastAPI()

# ✅ Snowflake connection (still using ENV variables for safety)
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "hpfcrwb-oh67940")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "MAKWANDECAREERS")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "Makwande@202530")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "AUTOAPPLY_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

# ✅ Job Model
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    country: str
    post_date: Optional[str]
    closing_date: Optional[str]
    job_url: Optional[str]
    description: Optional[str]

@app.get("/")
def read_root():
    return {"message": "Auto Apply App API is live and ready 🚀"}

# ✅ Fetch jobs with filters
@app.get("/jobs", response_model=List[Job])
def get_jobs(
    country: Optional[str] = None,
    location: Optional[str] = None,
    company: Optional[str] = None,
    title: Optional[str] = None
):
    conn = get_snowflake_connection()
    cur = conn.cursor()

    try:
        # ✅ Base query
        query = """
            SELECT ID, JOB_TITLE, COMPANY, LOCATION, COUNTRY, POST_DATE, CLOSING_DATE, JOB_URL, DESCRIPTION
            FROM MATCHED_JOBS
            WHERE 1=1
        """

        # ✅ Add filters dynamically
        params = []
        if country:
            query += " AND COUNTRY ILIKE %s"
            params.append(f"%{country}%")
        if location:
            query += " AND LOCATION ILIKE %s"
            params.append(f"%{location}%")
        if company:
            query += " AND COMPANY ILIKE %s"
            params.append(f"%{company}%")
        if title:
            query += " AND JOB_TITLE ILIKE %s"
            params.append(f"%{title}%")

        cur.execute(query, params)
        rows = cur.fetchall()

        jobs = [
            Job(
                id=row[0],
                title=row[1],
                company=row[2],
                location=row[3],
                country=row[4],
                post_date=str(row[5]) if row[5] else None,
                closing_date=str(row[6]) if row[6] else None,
                job_url=row[7],
                description=row[8]
            )
            for row in rows
        ]
        return jobs

    finally:
        cur.close()
        conn.close()








    
















