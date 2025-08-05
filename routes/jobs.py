# routes/jobs.py

from fastapi import APIRouter
from app._jobs import fetch_jobs_from_snowflake

router = APIRouter()

@router.get("/jobs", tags=["Jobs"])
def get_jobs():
    """
    Endpoint to get matched job listings from Snowflake.
    """
    return {"status": "success", "data": fetch_jobs_from_snowflake()}
