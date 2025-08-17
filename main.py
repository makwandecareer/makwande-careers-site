# main.py
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import os, datetime

app = FastAPI(title="AutoApply API")

# --- CORS (tighten to your domains later) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Serve frontend if present (frontend_build/index.html, jobs.html, etc.) ---
if os.path.isdir("frontend_build"):
    app.mount("/", StaticFiles(directory="frontend_build", html=True), name="static")

# --- Simple Jobs API (optional, works with your jobs.html) ---
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

JOBS: List[Job] = []

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()}

@app.get("/api/jobs", response_model=List[Job])
def list_jobs(q: Optional[str] = None, location: Optional[str] = None,
              company: Optional[str] = None, remote: Optional[bool] = None):
    def match(job: Job):
        if q:
            hay = f"{job.title} {job.company} {job.location} {job.country} {job.description}".lower()
            if q.lower() not in hay:
                return False
        if location and job.location != location:
            return False
        if company and job.company != company:
            return False
        if remote is not None and job.remote != remote:
            return False
        return True
    return [j for j in JOBS if match(j)]

@app.post("/api/jobs", response_model=Job)
def create_job(job: Job, x_api_key: Optional[str] = Header(None)):
    api_key = os.getenv("RECRUITER_API_KEY", "")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if not job.posted_at:
        job.posted_at = datetime.datetime.utcnow().isoformat()
    JOBS.insert(0, job)
    return job

