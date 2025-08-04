# FastAPI route to save employer exclusions per user
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Simulated database (replace with Snowflake or real DB later)
user_exclusions = {}
user_profiles = {}
posted_jobs = []
applied_jobs = []

class ExclusionRequest(BaseModel):
    exclusions: str
    user_email: Optional[str] = "anonymous"

class JobApplication(BaseModel):
    job_id: str
    company: str
    user_email: Optional[str] = "anonymous"

class JobPost(BaseModel):
    title: str
    description: str
    location: str
    posted_by: str

class EmployerRegistration(BaseModel):
    company: str
    email: str
    password: str

@app.post("/api/set_exclusions")
async def set_exclusions(data: ExclusionRequest):
    user_exclusions[data.user_email] = [x.strip().lower() for x in data.exclusions.split(",") if x.strip()]
    return {"message": "Exclusions updated.", "exclusions": user_exclusions[data.user_email]}

@app.get("/api/get_exclusions")
async def get_exclusions(user_email: str = "anonymous"):
    return {"exclusions": user_exclusions.get(user_email, [])}

@app.post("/api/apply_job")
async def apply_job(data: JobApplication):
    excluded_list = user_exclusions.get(data.user_email, [])
    for company in excluded_list:
        if company in data.company.lower():
            return {"message": f"Application skipped — {data.company} is in the exclusion list."}
    applied_jobs.append({"job_id": data.job_id, "company": data.company, "user": data.user_email})
    return {"message": "Application submitted successfully.", "job": data.job_id}

@app.post("/api/post_job")
async def post_job(job: JobPost):
    posted_jobs.append(job.dict())
    return {"message": "Job posted successfully.", "job": job.title}

@app.post("/api/register_employer")
async def register_employer(reg: EmployerRegistration):
    user_profiles[reg.email] = {"company": reg.company, "password": reg.password}
    return {"message": f"Employer account created for {reg.company}"}















    
















