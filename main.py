from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import snowflake.connector
from pydantic import BaseModel
import os

# ✅ Initialize FastAPI app
app = FastAPI(
    title="AutoApplyApp API",
    version="0.1.0",
    description="API for job listings from Snowflake"
)

# ✅ Allow all origins for now (we can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Snowflake Connection Details (move these to Render env vars later)
SNOWFLAKE_USER = "MAKWANDECAREERS"
SNOWFLAKE_PASSWORD = "Makwande@202530"
SNOWFLAKE_ACCOUNT = "hpfcrwb-oh67940"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "AUTOAPPLY_DB"
SNOWFLAKE_SCHEMA = "PUBLIC"

def get_snowflake_connection():
    """Create a Snowflake connection."""
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        return conn
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

# ✅ Data Model for Jobs
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str

# ✅ Root Endpoint
@app.get("/")
def read_root():
    return {"message": "🚀 AutoApplyApp API is live!"}

# ✅ Fetch Jobs Endpoint
@app.get("/jobs", response_model=list[Job])
def get_jobs():
    """Fetch jobs from Snowflake MATCHED_JOBS table."""
    conn = get_snowflake_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT ID, TITLE, COMPANY, LOCATION
            FROM MATCHED_JOBS
            LIMIT 20
        """)
        rows = cur.fetchall()
        jobs = []
        for row in rows:
            jobs.append({
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3]
            })
        return jobs
    except Exception as e:
        print(f"❌ Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching jobs")
    finally:
        cur.close()
        conn.close()

# ✅ Run locally for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





    
















