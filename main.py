"""
AutoApply Jobs API (Render-ready)

Set these env vars on Render:
  SNOWFLAKE_ACCOUNT=...
  SNOWFLAKE_USER=...
  SNOWFLAKE_PASSWORD=...
  SNOWFLAKE_ROLE=ACCOUNTADMIN
  SNOWFLAKE_WAREHOUSE=COMPUTE_WH
  SNOWFLAKE_DATABASE=AUTOAPPLY_DB
  SNOWFLAKE_SCHEMA=PUBLIC
  JOBS_TABLE=JOBS

  GITHUB_CSV_URL=https://raw.githubusercontent.com/<owner>/<repo>/main/jobs.csv
  SYNC_TOKEN=<long_random_hex>                  # protects /sync/github
  RECRUITER_API_KEY=<optional_api_key>          # protects POST /jobs (if set)
  CORS_ALLOW_ORIGINS=https://autoapply-makwandecareers.co.za,https://www.autoapply-makwandecareers.co.za
"""

import os
import csv
import io
import hashlib
from typing import List, Optional, Dict, Any

import httpx
import snowflake.connector
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

# ============== ENV ==============
SNOWFLAKE_ACCOUNT   = os.getenv("SNOWFLAKE_ACCOUNT", "")
SNOWFLAKE_USER      = os.getenv("SNOWFLAKE_USER", "")
SNOWFLAKE_PASSWORD  = os.getenv("SNOWFLAKE_PASSWORD", "")
SNOWFLAKE_ROLE      = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DATABASE  = os.getenv("SNOWFLAKE_DATABASE", "AUTOAPPLY_DB")
SNOWFLAKE_SCHEMA    = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
JOBS_TABLE          = os.getenv("JOBS_TABLE", "JOBS")

GITHUB_CSV_URL      = os.getenv("GITHUB_CSV_URL", "")
SYNC_TOKEN          = os.getenv("SYNC_TOKEN", "")
RECRUITER_API_KEY   = os.getenv("RECRUITER_API_KEY", "")

CORS_ALLOW = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()]

# ============== APP ==============
app = FastAPI(title="AutoApply Jobs API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Do NOT mount StaticFiles at "/" (static lives on a Render Static Site)

# ============== MODELS ==============
class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    country: Optional[str] = ""
    remote: bool = False
    description: str
    apply_url: HttpUrl
    closing_date: Optional[str] = ""
    posted_at: Optional[str] = None

# ============== SNOWFLAKE HELPERS ==============
def _snow():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        role=SNOWFLAKE_ROLE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )

def ensure_table():
    sql = f"""
    CREATE TABLE IF NOT EXISTS {JOBS_TABLE} (
      ID STRING PRIMARY KEY,
      TITLE STRING,
      COMPANY STRING,
      LOCATION STRING,
      COUNTRY STRING,
      REMOTE BOOLEAN,
      DESCRIPTION STRING,
      APPLY_URL STRING,
      CLOSING_DATE STRING,
      POSTED_AT TIMESTAMP_NTZ,
      INGESTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    );
    """
    with _snow() as con, con.cursor() as cur:
        cur.execute(sql)

def job_id_from(j: Dict[str, Any]) -> str:
    key = f"{j.get('title','').strip().lower()}|{j.get('company','').strip().lower()}|{j.get('apply_url','').strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def _b(v: Any) -> bool:
    return str(v).strip().lower() in {"true", "yes", "y", "1", "remote"}

def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    r = {(k or "").strip().lower(): (v or "") for k, v in row.items() if k is not None}
    return {
        "id": r.get("id") or job_id_from({
            "title": r.get("title", ""),
            "company": r.get("company", ""),
            "apply_url": r.get("apply_url") or r.get("url") or r.get("link", "")
        }),
        "title": r.get("title", "").strip(),
        "company": r.get("company", "").strip(),
        "location": r.get("location", "").strip(),
        "country": r.get("country", "").strip(),
        "remote": _b(r.get("remote", "")),
        "description": r.get("description") or r.get("desc", ""),
        "apply_url": (r.get("apply_url") or r.get("url") or r.get("link", "")).strip(),
        "closing_date": r.get("closing_date") or r.get("deadline", ""),
        "posted_at": r.get("posted_at") or r.get("date", ""),
    }

def upsert_jobs(jobs: List[Dict[str, Any]]) -> int:
    if not jobs:
        return 0
    ensure_table()
    sql = f"""
    MERGE INTO {JOBS_TABLE} t
    USING (SELECT
      %s AS ID,%s AS TITLE,%s AS COMPANY,%s AS LOCATION,%s AS COUNTRY,
      %s AS REMOTE,%s AS DESCRIPTION,%s AS APPLY_URL,%s AS CLOSING_DATE,
      TO_TIMESTAMP_NTZ(%s) AS POSTED_AT
    ) s
    ON t.ID = s.ID
    WHEN MATCHED THEN UPDATE SET
      TITLE=s.TITLE, COMPANY=s.COMPANY, LOCATION=s.LOCATION, COUNTRY=s.COUNTRY,
      REMOTE=s.REMOTE, DESCRIPTION=s.DESCRIPTION, APPLY_URL=s.APPLY_URL,
      CLOSING_DATE=s.CLOSING_DATE, POSTED_AT=s.POSTED_AT
    WHEN NOT MATCHED THEN INSERT
      (ID,TITLE,COMPANY,LOCATION,COUNTRY,REMOTE,DESCRIPTION,APPLY_URL,CLOSING_DATE,POSTED_AT)
      VALUES (s.ID,s.TITLE,s.COMPANY,s.LOCATION,s.COUNTRY,s.REMOTE,s.DESCRIPTION,s.APPLY_URL,s.CLOSING_DATE,s.POSTED_AT);
    """
    with _snow() as con, con.cursor() as cur:
        for j in jobs:
            cur.execute(sql, (
                j["id"], j["title"], j["company"], j["location"], j["country"],
                j["remote"], j["description"], j["apply_url"], j["closing_date"],
                j["posted_at"] or None
            ))
    return len(jobs)

def select_jobs(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    ensure_table()
    where, params = [], []
    if filters.get("q"):
        q = f"%{filters['q'].lower()}%"
        where.append("(LOWER(TITLE) LIKE %s OR LOWER(COMPANY) LIKE %s OR LOWER(LOCATION) LIKE %s OR LOWER(DESCRIPTION) LIKE %s)")
        params += [q, q, q, q]
    for k, col in (("location", "LOCATION"), ("company", "COMPANY"), ("country", "COUNTRY")):
        if filters.get(k):
            where.append(f"{col} = %s")
            params.append(filters[k])
    if filters.get("remote") is not None:
        where.append("REMOTE = %s")
        params.append(filters["remote"])
    sql = f"SELECT ID,TITLE,COMPANY,LOCATION,COUNTRY,REMOTE,DESCRIPTION,APPLY_URL,CLOSING_DATE,POSTED_AT FROM {JOBS_TABLE}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY POSTED_AT DESC NULLS LAST, INGESTED_AT DESC"
    if filters.get("limit"):
        sql += " LIMIT %s"
        params.append(int(filters["limit"]))
    with _snow() as con, con.cursor(snowflake.connector.DictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    for r in rows:
        if r.get("POSTED_AT"):
            r["POSTED_AT"] = r["POSTED_AT"].isoformat()
    return rows

# ============== CSV SYNC ==============
def run_github_sync() -> int:
    if not GITHUB_CSV_URL:
        return 0
    with httpx.Client(timeout=60.0) as client:
        r = client.get(GITHUB_CSV_URL, headers={"Accept": "text/csv"}, follow_redirects=True)
        r.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(r.text)))
    jobs = []
    for row in rows:
        j = normalize_row(row)
        if j["title"] and j["company"] and j["location"] and j["apply_url"] and j["description"]:
            jobs.append(j)
    return upsert_jobs(jobs)

# ============== CORE ROUTES (no prefix) ==============
@app.get("/health")
def health_root():
    return {"ok": True}

@app.get("/jobs")
def list_jobs_root(
    q: Optional[str] = None,
    location: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    remote: Optional[bool] = Query(default=None),
    limit: Optional[int] = 500,
):
    rows = select_jobs({"q": q, "location": location, "company": company,
                        "country": country, "remote": remote, "limit": limit})
    return [{
        "id": r["ID"], "title": r["TITLE"], "company": r["COMPANY"],
        "location": r["LOCATION"], "country": r["COUNTRY"],
        "remote": bool(r["REMOTE"]), "description": r["DESCRIPTION"],
        "apply_url": r["APPLY_URL"], "closing_date": r["CLOSING_DATE"],
        "posted_at": r["POSTED_AT"],
    } for r in rows]

@app.post("/jobs", response_model=Job)
def create_job_root(job: Job, x_api_key: Optional[str] = Header(None)):
    if RECRUITER_API_KEY and x_api_key != RECRUITER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    upsert_jobs([job.model_dump()])
    return job

def _require_sync_token(header_token: Optional[str], query_token: Optional[str]):
    token = header_token or query_token
    if SYNC_TOKEN and token != SYNC_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.api_route("/sync/github", methods=["GET", "POST"])
def sync_github_root(request: Request,
                     x_sync_token: Optional[str] = Header(None),
                     token: Optional[str] = None):
    _require_sync_token(x_sync_token, token)
    count = run_github_sync()
    return {"synced": count, "source": GITHUB_CSV_URL, "method": request.method}

# ============== COMPATIBILITY ALIASES (/api prefix) ==============
@app.get("/api/health")
def health_api():
    return health_root()

@app.get("/api/jobs")
def list_jobs_api(
    q: Optional[str] = None,
    location: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    remote: Optional[bool] = Query(default=None),
    limit: Optional[int] = 500,
):
    return list_jobs_root(q=q, location=location, company=company, country=country, remote=remote, limit=limit)

@app.post("/api/jobs", response_model=Job)
def create_job_api(job: Job, x_api_key: Optional[str] = Header(None)):
    return create_job_root(job, x_api_key)

@app.api_route("/api/sync/github", methods=["GET", "POST"])
def sync_github_api(request: Request,
                    x_sync_token: Optional[str] = Header(None),
                    token: Optional[str] = None):
    return sync_github_root(request, x_sync_token, token)

# ============== CLI one-off ==============
if __name__ == "__main__":
    print("Syncing from GitHub CSV...")
    print("Synced:", run_github_sync())
