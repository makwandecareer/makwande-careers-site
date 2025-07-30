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
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_VERSION()")
        version = cur.fetchone()
        return {"status": "connected", "snowflake_version": version[0]}
    except Exception as e:
        return {"status": "error", "details": str(e)}

@app.get("/jobs")
def get_jobs():
    """Fetch job listings from Snowflake"""
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
        cur = conn.cursor()

        # ✅ Adjust this query to match your Snowflake table
        cur.execute("""
            SELECT JOB_TITLE, COMPANY, LOCATION, POST_ADVERTISED_DATE, CLOSING_DATE
            FROM MATCHED_JOBS
            LIMIT 20
        """)
        
        rows = cur.fetchall()
        job_list = []
        for row in rows:
            job_list.append({
                "job_title": row[0],
                "company": row[1],
                "location": row[2],
                "post_advertised_date": row[3],
                "closing_date": row[4]
            })
        return {"jobs": job_list}
    except Exception as e:
        return {"status": "error", "details": str(e)}










