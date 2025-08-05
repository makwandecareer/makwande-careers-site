# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domain in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample Job Model
class Job(BaseModel):
    title: str
    company: str
    location: str
    match_score: float
    description: str

# Dummy job data
jobs_data = [
    {
        "title": "Data Analyst",
        "company": "Mak Tech",
        "location": "Cape Town",
        "match_score": 92.5,
        "description": "Analyze data trends and build dashboards."
    },
    {
        "title": "Software Engineer",
        "company": "Code Base Ltd",
        "location": "Johannesburg",
        "match_score": 89.1,
        "description": "Build scalable backend services in Python."
    },
    {
        "title": "Digital Marketing Manager",
        "company": "Adzone",
        "location": "Durban",
        "match_score": 85.7,
        "description": "Develop SEO/SEM marketing strategies."
    }
]

@app.get("/")
def read_root():
    return {"message": "Welcome to AutoApply API"}

@app.get("/api/jobs", response_model=List[Job])
def get_jobs():
    return jobs_data

# Run locally for testing
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)



















    
















