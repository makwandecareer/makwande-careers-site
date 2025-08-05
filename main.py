# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import jobs

app = FastAPI(
    title="AutoApplyApp API",
    version="1.0.0",
    description="API for fetching matched jobs and automating applications."
)

# CORS setup — allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "AutoApplyApp Backend is Live!"}

# Register the job routes
app.include_router(jobs.router, prefix="/api")




















    
















