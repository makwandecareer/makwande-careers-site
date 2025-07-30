from fastapi.responses import JSONResponse

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
        cur = conn.cursor()
        cur.execute("SELECT JOB_TITLE, COMPANY, LOCATION, SALARY_RANGE, DESCRIPTION FROM MATCHED_JOBS LIMIT 10;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        jobs = []
        for row in rows:
            jobs.append({
                "job_title": row[0],
                "company": row[1],
                "location": row[2],
                "salary_range": row[3],
                "description": row[4]
            })

        return JSONResponse(content={"jobs": jobs})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)










