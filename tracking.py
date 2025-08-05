from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import datetime

tracking_router = APIRouter()

# In-memory database (replace with real DB later)
applications_db = []
jobs_posted_db = []
employers_db = []

class Application(BaseModel):
    id: str
    user_email: str
    job_title: str
    company: str
    location: str
    status: str
    applied_on: str

class NewApplication(BaseModel):
    user_email: str
    job_title: str
    company: str
    location: str

class JobPost(BaseModel):
    employer_email: str
    job_title: str
    company: str
    location: str
    description: str
    post_date: str = datetime.datetime.now().strftime("%Y-%m-%d")

class Employer(BaseModel):
    name: str
    company_name: str
    email: str
    password: str

class StatusUpdate(BaseModel):
    application_id: str
    new_status: str

# Save new job application
@tracking_router.post("/api/save_application")
def save_application(payload: NewApplication):
    app_id = str(uuid4())
    applications_db.append(Application(
        id=app_id,
        user_email=payload.user_email,
        job_title=payload.job_title,
        company=payload.company,
        location=payload.location,
        status="Applied",
        applied_on=datetime.datetime.now().strftime("%Y-%m-%d")
    ))
    return {"message": "Application saved", "application_id": app_id}

# Get all applications by user
@tracking_router.get("/api/get_applications/{user_email}")
def get_applications(user_email: str):
    return [a for a in applications_db if a.user_email == user_email]

# Update application status
@tracking_router.post("/api/update_status")
def update_status(payload: StatusUpdate):
    for app in applications_db:
        if app.id == payload.application_id:
            app.status = payload.new_status
            return {"message": "Status updated"}
    raise HTTPException(status_code=404, detail="Application not found")

# Employer signup
@tracking_router.post("/api/employer_signup")
def employer_signup(payload: Employer):
    if any(e.email == payload.email for e in employers_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    employers_db.append(payload)
    return {"message": "Employer registered successfully"}

# Post a job
@tracking_router.post("/api/post_job")
def post_job(payload: JobPost):
    jobs_posted_db.append(payload)
    return {"message": "Job posted"}

# Get all applicants per job (by employer email)
@tracking_router.get("/api/list_applicants/{employer_email}")
def list_applicants(employer_email: str):
    return [a for a in applications_db if a.company in [
        j.company for j in jobs_posted_db if j.employer_email == employer_email
    ]]
