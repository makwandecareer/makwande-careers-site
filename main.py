from fastapi import FastAPI
import snowflake.connector
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AutoApplyApp FastAPI is live!"}

@app.get("/test-connection")
def test_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        return {"status": "connected", "snowflake_version": conn.version}
    except Exception as e:
        return {"status": "error", "details": str(e)}

@app.get("/jobs")
def get_jobs():
    """Fetch jobs from the MATCHED_JOBS table"""
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT JOB_TITLE, COMPANY, LOCATION, DESCRIPTION, JOB_SOURCE FROM MATCHED_JOBS LIMIT 50;")
        rows = cursor.fetchall()

        jobs_list = []
        for row in rows:
            jobs_list.append({
                "job_title": row[0],
                "company": row[1],
                "location": row[2],
                "description": row[3],
                "job_source": row[4]
            })
        cursor.close()
        conn.close()
        return {"jobs": jobs_list}
    except Exception as e:
        return {"error": str(e)}










