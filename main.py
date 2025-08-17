# main.py
import os, csv, io, hashlib
from typing import List, Optional, Dict, Any

import httpx
import snowflake.connector
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

# ===== ENV =====
SNOWFLAKE_ACCOUNT   = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER      = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD  = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ROLE      = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DATABASE  = os.getenv("SNOWFLAKE_DATABASE", "AUTOAPPLY_DB")
SNOWFLAKE_SCHEMA    = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
TABLE               = os.getenv("JOBS_TABLE", "JOBS")
GITHUB_CSV_URL      = os.getenv("GITHUB_CSV_URL", "")
SYNC_TOKEN          = os.getenv("SYNC_TOKEN", "")
CORS_ALLOW          = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()]

# ===== APP =====
app = FastAPI(title="AutoApply Jobs API")
app.add_middleware(CORSMiddleware,
    allow_origins=CORS_ALLOW or ["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# serve static if present (optional)
if os.path.isdir("frontend_build"):
    app.mount("/", StaticFiles(directory="frontend_build", html=True), name="static")

# ===== MODELS =====
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

# ===== SNOWFLAKE HELPERS =====
def _snow():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT, user=SNOWFLAKE_USER, password=SNOWFLAKE_PASSWORD,
        role=SNOWFLAKE_ROLE, warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE, schema=SNOWFLAKE_SCHEMA
    )

def ensure_table():
    sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE} (
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
    return str(v).strip().lower() in {"true","yes","y","1","remote"}

def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    r = {(k or "").lower().strip(): (v or "") for k, v in row.items() if k is not None}
    return {
        "id": r.get("id") or job_id_from({
            "title": r.get("title",""), "company": r.get("company",""),
            "apply_url": r.get("apply_url") or r.get("url") or r.get("link","")
        }),
        "title": r.get("title","").strip(),
        "company": r.get("company","").strip(),
        "location": r.get("location","").strip(),
        "country": r.get("country","").strip(),
        "remote": _b(r.get("remote","")),
        "description": r.get("description") or r.get("desc",""),
        "apply_url": (r.get("apply_url") or r.get("url") or r.get("link","")).strip(),
        "closing_date": r.get("closing_date") or r.get("deadline",""),
        "posted_at": r.get("posted_at") or r.get("date","")
    }

def upsert_jobs(jobs: List[Dict[str, Any]]) -> int:
    if not jobs: return 0
    ensure_table()
    sql = f"""
    MERGE INTO {TABLE} t
    USING (SELECT
        %s ID,%s TITLE,%s COMPANY,%s LOCATION,%s COUNTRY,%s REMOTE,%s DESCRIPTION,%s APPLY_URL,%s CLOSING_DATE,TO_TIMESTAMP_NTZ(%s) POSTED_AT
    ) s
    ON t.ID = s.ID
    WHEN MATCHED THEN UPDATE SET
      TITLE=s.TITLE, COMPANY=s.COMPANY, LOCATION=s.LOCATION, COUNTRY=s.COUNTRY,
      REMOTE=s.REMOTE, DESCRIPTION=s.DESCRIPTION, APPLY_URL=s.APPLY_URL,
      CLOSING_DATE=s.CLOSING_DATE, POSTED_AT=s.POSTED_AT
    WHEN NOT MATCHED THEN INSERT
      (ID, TITLE, COMPANY, LOCATION, COUNTRY, REMOTE, DESCRIPTION, APPLY_URL, CLOSING_DATE, POSTED_AT)
      VALUES (s.ID, s.TITLE, s.COMPANY, s.LOCATION, s.COUNTRY, s.REMOTE, s.DESCRIPTION, s.APPLY_URL, s.CLOSING_DATE, s.POSTED_AT);
    """
    with _snow() as con, con.cursor() as cur:
        for j in jobs:
            cur.execute(sql, (
                j["id"], j["title"], j["company"], j["location"], j["country"],
                j["remote"], j["description"], j["apply_url"], j["closing_date"],
                j["posted_at"] or None
            ))
    return len(jobs)

# ===== GITHUB CSV → SNOWFLAKE =====
def run_github_sync() -> int:
    """Fetch CSV from GITHUB_CSV_URL and upsert into Snowflake."""
    if not GITHUB_CSV_URL: return 0
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

# ===== API =====
@app.get("/api/health")
def health(): return {"ok": True}

@app.get("/api/jobs")
def list_jobs(
    q: Optional[str] = None,
    location: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    remote: Optional[bool] = Query(default=None),
    limit: Optional[int] = 500
):
    ensure_table()
    where, params = [], []
    if q:
        ql = f"%{q.lower()}%"
        where.append("(LOWER(TITLE) LIKE %s OR LOWER(COMPANY) LIKE %s OR LOWER(LOCATION) LIKE %s OR LOWER(DESCRIPTION) LIKE %s)")
        params += [ql, ql, ql, ql]
    for k, col in (("location","LOCATION"), ("company","COMPANY"), ("country","COUNTRY")):
        v = locals()[k]
        if v: where.append(f"{col} = %s"); params.append(v)
    if remote is not None: where.append("REMOTE = %s"); params.append(remote)

    sql = f"SELECT ID,TITLE,COMPANY,LOCATION,COUNTRY,REMOTE,DESCRIPTION,APPLY_URL,CLOSING_DATE,POSTED_AT FROM {TABLE}"
    if where: sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY POSTED_AT DESC NULLS LAST, INGESTED_AT DESC"
    if limit: sql += " LIMIT %s"; params.append(int(limit))

    with _snow() as con, con.cursor(snowflake.connector.DictCursor) as cur:
        cur.execute(sql, params); rows = cur.fetchall()
    for r in rows:
        if r.get("POSTED_AT"): r["POSTED_AT"] = r["POSTED_AT"].isoformat()
    return [
        {"id": r["ID"], "title": r["TITLE"], "company": r["COMPANY"], "location": r["LOCATION"],
         "country": r["COUNTRY"], "remote": bool(r["REMOTE"]), "description": r["DESCRIPTION"],
         "apply_url": r["APPLY_URL"], "closing_date": r["CLOSING_DATE"], "posted_at": r["POSTED_AT"]}
        for r in rows
    ]

@app.post("/api/jobs", response_model=Job)
def create_job(job: Job, x_api_key: Optional[str] = Header(None)):
    api_key = os.getenv("RECRUITER_API_KEY", "")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    upsert_jobs([job.model_dump()])
    return job

@app.post("/api/sync/github")
def sync_github(x_sync_token: Optional[str] = Header(None)):
    if SYNC_TOKEN and x_sync_token != SYNC_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    count = run_github_sync()
    return {"synced": count, "source": GITHUB_CSV_URL}
