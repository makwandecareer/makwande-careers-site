from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import snowflake.connector
import os

app = FastAPI()

# ✅ Snowflake connection function
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

# ✅ Job model for Create & Update
class Job(BaseModel):
    job_title: str
    company: str
    location: str
    description: str

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {"message": "AutoApplyApp FastAPI with CRUD is live!"}

# ✅ Get all jobs
@app.get("/jobs")
def get_jobs():
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT JOB_ID, JOB_TITLE, COMPANY, LOCATION, DESCRIPTION FROM MATCHED_JOBS")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        jobs = []
        for row in rows:
            jobs.append({
                "job_id": row[0],
                "job_title": row[1],
                "company": row[2],
                "location": row[3],
                "description": row[4]
            })
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Get a single job by ID
@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT JOB_ID, JOB_TITLE, COMPANY, LOCATION, DESCRIPTION FROM MATCHED_JOBS WHERE JOB_ID=%s", (job_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "job_id": row[0],
            "job_title": row[1],
            "company": row[2],
            "location": row[3],
            "description": row[4]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Create a new job
@app.post("/jobs")
def create_job(job: Job):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO MATCHED_JOBS (JOB_TITLE, COMPANY, LOCATION, DESCRIPTION)
            VALUES (%s, %s, %s, %s)
        """, (job.job_title, job.company, job.location, job.description))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Job created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Update an existing job
@app.put("/jobs/{job_id}")
def update_job(job_id: int, job: Job):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE MATCHED_JOBS 
            SET JOB_TITLE=%s, COMPANY=%s, LOCATION=%s, DESCRIPTION=%s
            WHERE JOB_ID=%s
        """, (job.job_title, job.company, job.location, job.description, job_id))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Job updated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Delete a job
@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM MATCHED_JOBS WHERE JOB_ID=%s", (job_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Job {job_id} deleted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))










