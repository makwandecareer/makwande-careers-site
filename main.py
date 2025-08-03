from fastapi import FastAPI, Query
from pydantic import BaseModel
import snowflake.connector
from typing import List, Optional

# Snowflake connection details
ACCOUNT = "hpfcrwb-oh67940"
USER = "MAKWANDECAREERS"
PASSWORD = "Makwande@202530"
WAREHOUSE = "COMPUTE_WH"
DATABASE = "AUTOAPPLY_DB"
SCHEMA = "PUBLIC"

# ✅ Supported SADC Countries
SADC_COUNTRIES = [
    "South Africa",
    "Lesotho",
    "Eswatini",
    "Botswana",
    "Namibia",
    "Zimbabwe",
    "Zambia",
    "Mozambique",
    "Angola",
    "Malawi"
]

# Initialize FastAPI
app = FastAPI(title="Auto Apply API", version="1.2.0")

# Job Model
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    post_date: str
    closing_date: str

# Snowflake Connection Function
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA
    )

@app.get("/jobs", response_model=List[Job])
def get_jobs(
    country: Optional[str] = Query(
        None,
        description="Filter by country",
        enum=SADC_COUNTRIES  # ✅ Dropdown on Swagger UI
    ),
    location: Optional[str] = Query(None, description="Filter by location (ILIKE search)"),
    sort: Optional[str] = Query("desc", description="Sort by post_date: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, le=100, description="Number of jobs per page (max 100)")
):
    """
    ✅ Fetch jobs from Snowflake with pagination, sorting, and filtering by country & location.
    """

    offset = (page - 1) * limit
    sort_order = "ASC" if sort.lower() == "asc" else "DESC"

    # ✅ Base query
    query = """
        SELECT ID, TITLE, COMPANY, LOCATION, POST_DATE, CLOSING_DATE
        FROM MATCHED_JOBS
    """

    # ✅ Filters
    filters = []
    if country:
        filters.append(f"COUNTRY = '{country}'")
    if location:
        filters.append(f"LOCATION ILIKE '%{location}%'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += f" ORDER BY POST_DATE {sort_order} LIMIT {limit} OFFSET {offset}"

    # ✅ Connect to Snowflake and run query
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # ✅ Map to Job schema
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

    cursor.close()
    conn.close()

    return jobs

@app.get("/")
def read_root():
    return {"message": "✅ Auto Apply API - Jobs across 10 SADC countries with pagination, sorting & filters"}










    
















