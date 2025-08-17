# main.py
import os
import io
import csv
import hashlib
import datetime
from typing import List, Optional

import requests
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------
# Environment
# ----------------------------
SYNC_TOKEN = os.getenv("SYNC_TOKEN", "")
GITHUB_CSV_URL = os.getenv("GITHUB_CSV_URL", "")

SNOWFLAKE_ACCOUNT   = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER      = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD  = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DATABASE  = os.getenv("SNOWFLAKE_DATABASE", "AUTOAPPLY")
SNOWFLAKE_SCHEMA    = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")

USE_SNOWFLAKE = all([SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD])

# In-memory fallback store if Snowflake is not configured
JOBS_MEM: List[dict] = []

# ----------------------------
# FastAPI app + CORS
# ----------------------------
app = FastAPI(title="AutoApply Jobs API")

cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "")
cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ----------------------------
# Helpers
# ----------------------------
def _row_hash(title: str, company: str, apply_url: str) -> str:
    raw = f"{(title or '').lower()}|{(company or '').lower()}|{(apply_url or '').lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _parse_bool(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    return s in ("1", "true", "yes", "y")

def _parse_date(v):
    if not v:
        return None
    try:
        # allow ISO date or datetime
        if "t" in str(v).lower():
            return datetime.datetime.fromisoformat(str(v).replace("Z", ""))
        return datetime.date.fromisoformat(str(v))
    except Exception:
        return None

REQUIRED_HEADERS = {
    "title",
    "company",
    "location",
    "description",
    "apply_url",
    "country",
    "remote",
    "closing_date",
    "posted_at",
}

def _csv_to_jobs(csv_text: str, source="github") -> List[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    headers = {h.strip().lower() for h in (reader.fieldnames or [])}
    if not REQUIRED_HEADERS.issubset(headers):
        missing = sorted(list(REQUIRED_HEADERS - headers))
        raise HTTPException(status_code=400, detail=f"CSV missing headers: {missing}")

    out: List[dict] = []
    for r in reader:
        job = {
            "title":        (r.get("title") or "").strip(),
            "company":      (r.get("company") or "").strip(),
            "location":     (r.get("location") or "").strip(),
            "description":  (r.get("description") or "").strip(),
            "apply_url":    (r.get("apply_url") or "").strip(),
            "country":      ((r.get("country") or "").strip().upper() or None),
            "remote":       _parse_bool(r.get("remote")),
            "closing_date": _parse_date(r.get("closing_date")),
            "posted_at":    _parse_date(r.get("posted_at")),
            "source":       source,
        }
        job["hash"] = _row_hash(job["title"], job["company"], job["apply_url"])
        out.append(job)
    return out

# ----------------------------
# Snowflake helpers (lazy import)
# ----------------------------
def _sf_conn():
    import snowflake.connector  # imported only if needed
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )

def _sf_merge_jobs(jobs: List[dict]) -> int:
    if not jobs:
        return 0
    conn = _sf_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS JOBS (
              ID STRING,
              TITLE STRING,
              COMPANY STRING,
              LOCATION STRING,
              DESCRIPTION STRING,
              APPLY_URL STRING,
              COUNTRY STRING,
              REMOTE BOOLEAN,
              CLOSING_DATE DATE,
              POSTED_AT TIMESTAMP_NTZ,
              SOURCE STRING,
              HASH STRING,
              CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
        )
        cur.execute("CREATE TEMP TABLE TMP_JOBS LIKE JOBS")

        insert_sql = """
            INSERT INTO TMP_JOBS
              (ID, TITLE, COMPANY, LOCATION, DESCRIPTION, APPLY_URL,
               COUNTRY, REMOTE, CLOSING_DATE, POSTED_AT, SOURCE, HASH)
            SELECT :id, :title, :company, :location, :description, :apply_url,
                   :country, :remote, :closing_date, :posted_at, :source, :hash
        """
        for j in jobs:
            cur.execute(
                insert_sql,
                {
                    "id": hashlib.md5(j["hash"].encode()).hexdigest(),
                    "title": j["title"],
                    "company": j["company"],
                    "location": j["location"],
                    "description": j["description"],
                    "apply_url": j["apply_url"],
                    "country": j["country"],
                    "remote": j["remote"],
                    "closing_date": j["closing_date"],
                    "posted_at": j["posted_at"],
                    "source": j["source"],
                    "hash": j["hash"],
                },
            )

        cur.execute(
            """
            MERGE INTO JOBS t
            USING TMP_JOBS s
            ON t.HASH = s.HASH
            WHEN MATCHED THEN UPDATE SET
              TITLE=s.TITLE, COMPANY=s.COMPANY, LOCATION=s.LOCATION,
              DESCRIPTION=s.DESCRIPTION, APPLY_URL=s.APPLY_URL,
              COUNTRY=s.COUNTRY, REMOTE=s.REMOTE, CLOSING_DATE=s.CLOSING_DATE,
              POSTED_AT=s.POSTED_AT, SOURCE=s.SOURCE
            WHEN NOT MATCHED THEN INSERT
              (ID, TITLE, COMPANY, LOCATION, DESCRIPTION, APPLY_URL,
               COUNTRY, REMOTE, CLOSING_DATE, POSTED_AT, SOURCE, HASH)
            VALUES
              (s.ID, s.TITLE, s.COMPANY, s.LOCATION, s.DESCRIPTION, s.APPLY_URL,
               s.COUNTRY, s.REMOTE, s.CLOSING_DATE, s.POSTED_AT, s.SOURCE, s.HASH)
            """
        )
        cur.execute("SELECT COUNT(*) FROM TMP_JOBS")
        count = int(cur.fetchone()[0])
        conn.commit()
        return count
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

def _sf_query_jobs(q: Optional[str], limit: int) -> List[dict]:
    conn = _sf_conn()
    cur = conn.cursor()
    try:
        base = """
            SELECT TITLE, COMPANY, LOCATION, DESCRIPTION, APPLY_URL,
                   COUNTRY, REMOTE, CLOSING_DATE, POSTED_AT, SOURCE
            FROM JOBS
        """
        params = {}
        if q:
            base += " WHERE LOWER(TITLE) LIKE :q OR LOWER(COMPANY) LIKE :q OR LOWER(LOCATION) LIKE :q"
            params["q"] = f"%{q.lower()}%"
        base += " ORDER BY COALESCE(POSTED_AT, CREATED_AT) DESC LIMIT :lim"
        params["lim"] = limit
        cur.execute(base, params)
        cols = [c[0].lower() for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def root():
    return {"ok": True, "snowflake": USE_SNOWFLAKE}

@app.get("/api/health")
def health():
    return {"ok": True, "snowflake": USE_SNOWFLAKE}

@app.get("/api/jobs")
def get_jobs(q: Optional[str] = Query(None), limit: int = 200):
    limit = max(1, min(int(limit), 1000))
    if USE_SNOWFLAKE:
        return _sf_query_jobs(q, limit)

    # in-memory fallback
    if q:
        qq = q.lower()
        data = [
            j for j in JOBS_MEM
            if qq in j["title"].lower()
            or qq in j["company"].lower()
            or qq in j["location"].lower()
        ]
        return data[:limit]
    return JOBS_MEM[:limit]

def _ingest_from_csv_text(csv_text: str) -> int:
    jobs = _csv_to_jobs(csv_text, source="github")
    if USE_SNOWFLAKE:
        return _sf_merge_jobs(jobs)
    else:
        global JOBS_MEM
        JOBS_MEM = jobs
        return len(jobs)

@app.get("/api/sync/github")
def sync_github_get(token: str):
    if token != SYNC_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")
    if not GITHUB_CSV_URL:
        raise HTTPException(status_code=400, detail="GITHUB_CSV_URL not set")
    r = requests.get(GITHUB_CSV_URL, timeout=30)
    r.raise_for_status()
    n = _ingest_from_csv_text(r.text)
    return {"synced": n, "source": "Snowflake" if USE_SNOWFLAKE else "memory", "method": "GET"}

@app.post("/api/sync/github")
def sync_github_post(x_sync_token: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    # accept either header "X-Sync-Token" or query ?token=
    t = x_sync_token or token or ""
    if t != SYNC_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")
    if not GITHUB_CSV_URL:
        raise HTTPException(status_code=400, detail="GITHUB_CSV_URL not set")
    r = requests.get(GITHUB_CSV_URL, timeout=30)
    r.raise_for_status()
    n = _ingest_from_csv_text(r.text)
    return {"synced": n, "source": "Snowflake" if USE_SNOWFLAKE else "memory", "method": "POST"}

# ----------------------------
# Uvicorn entrypoint
# ----------------------------
if _name_ == "_main_":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


