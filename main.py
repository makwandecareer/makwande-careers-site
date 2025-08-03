from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import snowflake.connector
from typing import List, Optional

# ✅ Snowflake connection details
ACCOUNT = "hpfcrwb-oh67940"
USER = "MAKWANDECAREERS"
PASSWORD = "Makwande@202530"
WAREHOUSE = "COMPUTE_WH"
DATABASE = "AUTOAPPLY_DB"
SCHEMA = "PUBLIC"

# ✅ Supported SADC Countries
SADC_COUNTRIES = [
    "South Africa", "Lesotho", "Eswatini", "Botswana", "Namibia",
    "Zimbabwe", "Zambia", "Mozambique", "Angola", "Malawi"
]

# ✅ Supported Job Levels
JOB_LEVELS = [
    "Learnership",
    "Internship",
    "Entry Level",
    "Post Graduate Level",
    "Senior Position"
]

# ✅ Initialize FastAPI
app = FastAPI(
    title="Auto Apply API",
    version="2.0.0",
    description="✅ Final API powering AutoApply across 10 SADC countries with full CRUD for jobs."
)

# ✅ Job Model for responses
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    country: str
    industry: Optional[str]
    job_level: Optional[str]
    post_date: str
    closing_date: str

# ✅ JobCreate Model for POST requests
class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    country: str
    industry: Optional[str] = None
    job_level: Optional[str] = Query(None, enum=JOB_LEVELS)
    post_date: str
    closing_date: str

# ✅ Snowflake Connection Function
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA
    )

# ✅ Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AutoApply API", "version": "2.0.0"}

# ✅ Countries Endpoint
@app.get("/countries")
def get_countries():
    return {"supported_countries": SADC_COUNTRIES}

# ✅ Jobs Endpoint (Fetch)
@app.get("/jobs", response_model=List[Job])
def get_jobs(
    country: str = Query(
        "South Africa",
        description="Filter by country (default = South Africa)",
        enum=SADC_COUNTRIES
    ),
    location: Optional[str] = Query(None, description="Filter by location (ILIKE search)"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    job_level: Optional[str] = Query(None, description="Filter by job level", enum=JOB_LEVELS),
    sort: Optional[str] = Query("desc", description="Sort by post_date: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, le=100, description="Number of jobs per page (max 100)")
):
    offset = (page - 1) * limit
    sort_order = "ASC" if sort.lower() == "asc" else "DESC"

    query = """
        SELECT ID, TITLE, COMPANY, LOCATION, COUNTRY, INDUSTRY, JOB_LEVEL, POST_DATE, CLOSING_DATE
        FROM MATCHED_JOBS
    """

    filters = [f"COUNTRY = '{country}'"]
    if location:
        filters.append(f"LOCATION ILIKE '%{location}%'")
    if industry:
        filters.append(f"INDUSTRY ILIKE '%{industry}%'")
    if job_level:
        filters.append(f"JOB_LEVEL = '{job_level}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += f" ORDER BY POST_DATE {sort_order} LIMIT {limit} OFFSET {offset}"

    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    jobs = []
    for row in rows:
        jobs.append({
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "country": row[4],
            "industry": row[5],
            "job_level": row[6],
            "post_date": str(row[7]),
            "closing_date": str(row[8])
        })

    cursor.close()
    conn.close()

    return jobs

# ✅ Jobs Endpoint (POST - Add new job)
@app.post("/jobs")
def add_job(job: JobCreate):
    """
    ✅ Add a new job posting to Snowflake MATCHED_JOBS table.
    """
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO MATCHED_JOBS (TITLE, COMPANY, LOCATION, COUNTRY, INDUSTRY, JOB_LEVEL, POST_DATE, CLOSING_DATE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            job.title,
            job.company,
            job.location,
            job.country,
            job.industry,
            job.job_level,
            job.post_date,
            job.closing_date
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "✅ Job added successfully", "job": job}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting job: {str(e)}")

# ✅ Root Endpoint
@app.get("/")
def read_root():
    return {
        "message": "✅ Auto Apply API FINAL VERSION (v2.0.0)",
        "features": [
            "Jobs fetch with filters, pagination & sorting",
            "Add jobs via POST",
            "Health check",
            "List of supported countries"
        ],
        "default_country": "South Africa",
        "endpoints": ["/jobs (GET & POST)", "/countries", "/health"]
    }












    
















