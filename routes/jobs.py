# routes/jobs.py

import os
from fastapi import APIRouter
from snowflake import connector
from typing import List

router = APIRouter()

@router.get("/")
def fetch_jobs():
    try:
        conn = connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM MATCHED_JOBS LIMIT 10;")
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        jobs = [dict(zip(columns, row)) for row in results]
        cursor.close()
        conn.close()
        return {"jobs": jobs}
    except Exception as e:
        return {"error": str(e)}

