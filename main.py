from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/matched_jobs")
def matched_jobs():
    # Replace this with your Snowflake fetching logic if needed
    return {
        "jobs": [
            {"title": "Software Engineer", "company": "Tech Inc", "location": "Cape Town", "match_score": 93},
            {"title": "Data Analyst", "company": "DataWorks", "location": "Johannesburg", "match_score": 88}
        ]
    }
























    
















