# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import jobs  # Import your route module

app = FastAPI(
    title="AutoApply API",
    description="Backend API for job matching and automation",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home route
@app.get("/")
def read_root():
    return {"message": "Welcome to the AutoApply API 🚀"}

# Include jobs route
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])





















    
















