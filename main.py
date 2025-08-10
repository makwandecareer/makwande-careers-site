# main.py
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# ------------------------------------------------------------------------------
# App metadata
# ------------------------------------------------------------------------------
APP_NAME = "AutoApply API"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# ------------------------------------------------------------------------------
# Allowed CORS origins
#   - You can override with env var ALLOWED_ORIGINS (comma-separated)
# ------------------------------------------------------------------------------
_default_origins: List[str] = [
    "https://autoapplyapp-mobile.onrender.com",  # your static site on Render
    "https://autoapply-api.onrender.com",        # this API's Render URL
    "https://makwandecareer.co.za",              # your custom domain (if used)
]

_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _allowed_origins_env:
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]
else:
    ALLOWED_ORIGINS = _default_origins

# ------------------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------------------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Backend API for AutoApply (signup, login, jobs).",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# In-memory "db" (demo only). Replace with a real DB in production.
# ------------------------------------------------------------------------------
_users_by_email: Dict[str, Dict] = {}
_fake_jobs: List[Dict] = [
    {
        "id": "job-001",
        "title": "Junior Software Engineer",
        "company": "Makwandé Careers",
        "location": "Remote",
        "posted_at": datetime.utcnow().isoformat() + "Z",
        "apply_url": "https://makwandecareer.co.za/jobs/junior-software-engineer",
    },
    {
        "id": "job-002",
        "title": "Data Analyst Intern",
        "company": "Makwandé Careers",
        "location": "Frankfurt, DE (Hybrid)",
        "posted_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
        "apply_url": "https://makwandecareer.co.za/jobs/data-analyst-intern",
    },
]

# ------------------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------------------
class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class AuthResponse(BaseModel):
    message: str
    token: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    posted_at: str
    apply_url: str

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.get("/", summary="Health check")
def health():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
    }

@app.post("/api/signup", response_model=AuthResponse, summary="Create a new account")
def signup(payload: SignupRequest):
    email_key = payload.email.lower()
    if email_key in _users_by_email:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    # Store user (hashing omitted for demo)
    _users_by_email[email_key] = {
        "full_name": payload.full_name,
        "email": email_key,
        "password": payload.password,  # NEVER store plain text in production
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    # Return a fake token (replace with real JWT in production)
    token = f"fake-jwt-token-for:{email_key}"
    return AuthResponse(message="Signup successful.", token=token)

@app.post("/api/login", response_model=AuthResponse, summary="Login")
def login(payload: LoginRequest):
    email_key = payload.email.lower()
    user = _users_by_email.get(email_key)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = f"fake-jwt-token-for:{email_key}"
    return AuthResponse(message="Login successful.", token=token)

@app.get("/api/jobs", response_model=List[Job], summary="List jobs")
def list_jobs():
    """
    Returns a demo list of jobs. Replace with your real source:
    - pull from a database
    - or fetch from your external job source using requests/httpx
    """
    return _fake_jobs

# Optional: catch-all for unknown API paths (keeps errors clean)
@app.middleware("http")
async def not_found_passthrough(request, call_next):
    response = await call_next(request)
    return response

# ------------------------------------------------------------------------------
# Dev/local run (Render uses start command, but this is safe and correct)
# ------------------------------------------------------------------------------
if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


















































    
















