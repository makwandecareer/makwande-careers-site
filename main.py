import os
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ----------------------------
# Models
# ----------------------------
class Health(BaseModel):
    ok: bool
    service: str = "autoapply-api"
    version: str = "1.0.0"

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    url: str
    posted_at: Optional[str] = None  # ISO string

# ----------------------------
# App
# ----------------------------
app = FastAPI(title="AutoApply API", version="1.0.0")

# Open CORS (frontend is on a different domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to your static site later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")

# ----------------------------
# Health
# ----------------------------
@app.get("/health", response_model=Health, tags=["Health"])
@router.get("/health", response_model=Health, tags=["Health"])
def health() -> Health:
    return Health(ok=True)

# ----------------------------
# Snowflake helpers (optional)
# ----------------------------
def _snowflake_env_ok() -> bool:
    needed = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    ]
    return all(os.getenv(k) for k in needed)

def _fetch_jobs_from_snowflake(limit: int = 50) -> List[Job]:
    """
    Query Snowflake if env is configured and connector is available.
    Expects a table or view JOBS with columns:
      ID, TITLE, COMPANY, LOCATION, URL, POSTED_AT
    """
    if not _snowflake_env_ok():
        return []

    try:
        import snowflake.connector  # type: ignore
    except Exception:
        # connector not installed — return empty and fall back
        return []

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
    try:
        sql = f"""
            SELECT ID, TITLE, COMPANY, LOCATION, URL, POSTED_AT
            FROM JOBS
            ORDER BY COALESCE(POSTED_AT, CURRENT_TIMESTAMP()) DESC
            LIMIT {int(limit)}
        """
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        jobs: List[Job] = []
        for r in rows:
            jid, title, company, location, url, posted = r
            jobs.append(
                Job(
                    id=str(jid),
                    title=title,
                    company=company,
                    location=location,
                    url=url,
                    posted_at=posted.isoformat() if posted else None,
                )
            )
        return jobs
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ----------------------------
# Fallback demo jobs
# ----------------------------
_DEMO_JOBS: List[Job] = [
    Job(
        id="demo-1",
        title="Junior Data Analyst",
        company="Acme Corp",
        location="Remote",
        url="https://example.com/jobs/1",
        posted_at=datetime.utcnow().isoformat(timespec="seconds"),
    ),
    Job(
        id="demo-2",
        title="Software Engineer (Python)",
        company="Globex",
        location="Frankfurt",
        url="https://example.com/jobs/2",
        posted_at=datetime.utcnow().isoformat(timespec="seconds"),
    ),
]

def _get_jobs(limit: int = 50) -> List[Job]:
    jobs = _fetch_jobs_from_snowflake(limit)
    if jobs:
        return jobs
    # No Snowflake data? Return a small list so the UI works.
    return _DEMO_JOBS[:limit]

# ----------------------------
# Jobs endpoints (both /api/jobs and /jobs)
# ----------------------------
@app.get("/jobs", response_model=List[Job], tags=["List Jobs"])
@router.get("/jobs", response_model=List[Job], tags=["List Jobs"])
def list_jobs(limit: int = 50) -> List[Job]:
    return _get_jobs(limit)

# ----------------------------
# Include router and root
# ----------------------------
app.include_router(router)

@app.get("/", tags=["Root"])
def root():
    return {"ok": True, "service": "autoapply-api"}

# ----------------------------
# Local dev
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

