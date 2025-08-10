# main.py
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# -------- App metadata --------
APP_NAME = "AutoApply API"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# -------- CORS --------
# Default origins you actually use. Add/remove as needed.
_default_origins: List[str] = [
    "https://autoapplyapp-mobile.onrender.com",
    "https://makwandecareer.co.za",
]

# Optional: allow overrides via env var
_allowed = os.getenv("ALLOWED_ORIGINS", "").strip()
ALLOWED_ORIGINS: List[str] = (
    [o.strip() for o in _allowed.split(",")] if _allowed else _default_origins
)

# -------- FastAPI app (docs explicitly enabled) --------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# -------- Middleware --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Schemas --------
class SignupData(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

# -------- Routes --------
@app.get("/")
def root():
    return {"ok": True, "service": APP_NAME, "version": APP_VERSION}

@app.get("/healthz")
def healthz():
    return {"status": "healthy"}

@app.post("/signup")
def signup(data: SignupData):
    # TODO: replace with real user creation (DB)
    # For now we just simulate success.
    return {"status": "success", "message": f"user {data.email} created"}

@app.post("/login")
def login(data: LoginData):
    # TODO: replace with real auth check
    if not data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"status": "success", "message": "logged in", "token": "dummy-token"}

@app.get("/jobs")
def jobs():
    # TODO: replace with real jobs query
    return {
        "jobs": [
            {"id": 1, "title": "Frontend Developer", "location": "Remote"},
            {"id": 2, "title": "Data Analyst", "location": "Cape Town"},
        ]
    }

# NOTE: No _name_ block, no main(), no uvicorn.run().
# Render will start it via your Start Command (uvicorn main:app ...).





















































    
















