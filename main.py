from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response  # ✅ Add this

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://auto-apply-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = [
    {"id": 1, "title": "Software Engineer", "company": "TechCorp", "location": "South Africa"},
    {"id": 2, "title": "Data Scientist", "company": "DataWorks", "location": "Namibia"}
]

@app.get("/")
def read_root():
    return {"message": "Auto Apply API is running and secure."}

# ✅ Fix for HEAD error
@app.head("/")
def head_root():
    return Response(status_code=200)

@app.get("/api/jobs")
def get_jobs():
    return {"jobs": jobs}






























    
















