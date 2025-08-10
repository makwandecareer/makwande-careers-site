# main.py
import os
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# -----------------------------------------------------------------------------
# App metadata
# -----------------------------------------------------------------------------
APP_NAME = "AutoApply API"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# -----------------------------------------------------------------------------
# Allowed CORS origins
# - Set env var ALLOWED_ORIGINS to a comma-separated list of URLs.
# - We also provide safe defaults that match your static site(s)/domain(s).
# -----------------------------------------------------------------------------
_default_origins = [
    "https://autoapplyapp-mobile.onrender.com",  # your Render static site
    "https://autoapplyapp.onrender.com",         # if you keep a second static site
    "https://makwandecareer.co.za",              # your custom domain (if used)
]

_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if _allowed_origins_env.strip():
    ALLOWED_ORIGINS: List[str] = [
        o.strip() for o in _allowed_origins_env.split(",") if o.strip()
    ]
else:
    ALLOWED_ORIGINS = _default_origins

# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",        # Swagger
    redoc_url="/redoc",      # ReDoc
    openapi_url="/openapi.json",
)

# -----------------------------------------------------------------------------
# CORS (this is the bit that fixes your front-end requests)
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # *critical*
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Health & meta endpoints
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    version: str
    origins: List[str]

@app.get("/", tags=["meta"])
def root():
    return {"name": APP_NAME, "version": APP_VERSION, "docs": "/docs"}

@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    return HealthResponse(status="ok", version=APP_VERSION, origins=ALLOWED_ORIGINS)

@app.get("/api/version", tags=["meta"])
def version():
    return {"version": APP_VERSION}

# -----------------------------------------------------------------------------
# Try to include your existing routers (preferred if you already have them)
#   - routes/auth.py   -> router with /signup, /login under /auth
#   - routes/jobs.py   -> router with /jobs under /api
# If they don't exist, we provide minimal fallbacks so the API still runs.
# -----------------------------------------------------------------------------
# AUTH ROUTES
_auth_router_included = False
try:
    from routes.auth import router as auth_router  # type: ignore
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    _auth_router_included = True
except Exception:
    # Minimal fallbacks (you can remove these if you have real routes)
    class SignupIn(BaseModel):
        email: str
        password: str
        name: Optional[str] = None

    class LoginIn(BaseModel):
        email: str
        password: str

    class AuthOut(BaseModel):
        message: str

    @app.post("/auth/signup", response_model=AuthOut, tags=["auth"])
    def fallback_signup(payload: SignupIn):
        # Replace with your real DB logic
        return AuthOut(message=f"Signup OK for {payload.email} (fallback)")

    @app.post("/auth/login", response_model=AuthOut, tags=["auth"])
    def fallback_login(payload: LoginIn):
        # Replace with your real auth/JWT logic
        return AuthOut(message=f"Login OK for {payload.email} (fallback)")

# JOBS ROUTES
_jobs_router_included = False
try:
    from routes.jobs import router as jobs_router  # type: ignore
    app.include_router(jobs_router, prefix="/api", tags=["jobs"])
    _jobs_router_included = True
except Exception:
    # Minimal fallback
    class Job(BaseModel):
        id: int
        title: str
        company: str
        location: str

    _SAMPLE_JOBS = [
        Job(id=1, title="Software Engineer", company="Makwandecareer", location="Remote"),
        Job(id=2, title="Data Analyst", company="AutoApply", location="Cape Town"),
    ]

    @app.get("/api/jobs", response_model=List[Job], tags=["jobs"])
    def fallback_jobs():
        return _SAMPLE_JOBS

# -----------------------------------------------------------------------------
# Optional: log which routers are active (handy in Render logs)
# -----------------------------------------------------------------------------
if not _auth_router_included:
    print("[INFO] Using fallback /auth routes (routes/auth.py not found).")
else:
    print("[INFO] Included routes/auth.py router at /auth.")

if not _jobs_router_included:
    print("[INFO] Using fallback /api/jobs route (routes/jobs.py not found).")
else:
    print("[INFO] Included routes/jobs.py router at /api.")

# -----------------------------------------------------------------------------
# Local dev entry point (Render uses Gunicorn/Uvicorn worker; this is for local)
# -----------------------------------------------------------------------------
if _name_ == "_main_":
    import uvicorn
    # Bind to 0.0.0.0 so it behaves like Render dyno locally
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)


















































    
















