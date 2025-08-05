from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Secure CORS: only allow your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://auto-apply-app.vercel.app"],  # Replace with your actual deployed frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy job list to test job endpoint
jobs = [
    {"id": 1, "title": "Software Engineer", "company": "TechCorp", "location": "South Africa"},
    {"id": 2, "title": "Data Scientist", "company": "DataWorks", "location": "Namibia"}
]

@app.get("/")
def read_root():
    return {"message": "Auto Apply API is running and secure."}

@app.get("/api/jobs")
def get_jobs():
    return {"jobs": jobs}

# Other API routes can be added later





























    
















