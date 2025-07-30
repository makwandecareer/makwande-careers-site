from fastapi import FastAPI
import snowflake.connector
import os

# ✅ Create FastAPI instance FIRST
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
        version = conn.cursor().execute("SELECT CURRENT_VERSION()").fetchone()
        return {"status": "connected", "snowflake_version": version[0]}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@app.get("/jobs")
def get_jobs():
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
        cursor.execute("SELECT * FROM MATCHED_JOBS LIMIT 10")
        rows = cursor.fetchall()

        jobs = []
        for row in rows:
            jobs.append({
                "job_title": row[0],
                "location": row[1],
                "salary": row[2],
                "job_source": row[3],
                "description": row[4]
            })

        return {"jobs": jobs}
    except Exception as e:
        return {"status": "failed", "error": str(e)}










