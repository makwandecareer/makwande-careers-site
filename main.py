import os
<<<<<<< HEAD
from typingfrom fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Auto Apply API",
    description="Backend API for Auto Apply App",
    version="1.0.0",
    docs_url="/docs",          # Ensure this is set
    redoc_url="/redoc"         # Optional
)

origins = [
    "https://autoapplyapp-mobile.onrender.com",
    # Add other frontend URLs if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
=======
import secrets
import hashlib
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


# ------------------------------------------------------------------------------
# App & CORS
# ------------------------------------------------------------------------------

app = FastAPI(title="AutoApply API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://autoapplyapp-mobile.onrender.com")

_allowed_origins = {
    FRONTEND_URL,
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_allowed_origins),
    allow_origin_regex=r"https://.*\.onrender\.com",
>>>>>>> 5d2161f (Fix CORS, add full API with signup, login, jobs endpoints)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
@app.get("/health")
def health_check():
    return {"status": "ok"}
=======

# ------------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

engine = None
if DATABASE_URL:
    try:
        # Example URL: postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
    except Exception as e:
        # We keep the app alive even if DB init fails, so /docs still loads.
        print("DB engine init error:", repr(e))


def db_exec(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute SQL (read/write). Returns list of rows as dicts for SELECT;
    empty list for non-SELECT.
    """
    if engine is None:
        raise HTTPException(
            status_code=500, detail="Database is not configured (missing DATABASE_URL)."
        )
    with engine.begin() as conn:
        res = conn.execute(text(sql), params or {})
        try:
            rows = res.mappings().all()
            return [dict(r) for r in rows]
        except Exception:
            return []


def bootstrap_users_table() -> None:
    """
    Create a very simple 'users' table if it doesn't exist.
    Only includes columns needed for demo auth flows.
    """
    if engine is None:
        return
    create_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    db_exec(create_sql)


def bootstrap_jobs_table_hint() -> None:
    """
    We won't create jobs automatically (you may already have one),
    but we'll detect its presence and handle when it doesn't exist.
    """
    pass


@app.on_event("startup")
def on_startup() -> None:
    try:
        bootstrap_users_table()
        bootstrap_jobs_table_hint()
    except OperationalError as e:
        print("Startup DB error:", repr(e))


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class JobOut(BaseModel):
    id: Optional[int]
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[datetime] = None


# ------------------------------------------------------------------------------
# Helpers (passwords)
# ------------------------------------------------------------------------------

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + password).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------

@app.get("/", tags=["health"])
def read_root():
    return {"status": "API is running", "frontend": FRONTEND_URL}


@app.get("/health", tags=["health"])
def health():
    # Basic DB ping if configured
    if engine is None:
        return {"ok": True, "db": "not-configured"}
    try:
        db_exec("SELECT 1;")
        return {"ok": True, "db": "ok"}
    except Exception as e:
        return {"ok": False, "db": repr(e)}


@app.post("/signup", tags=["auth"])
def signup(payload: SignupIn):
    # Check if user exists
    rows = db_exec("SELECT id FROM users WHERE email = :email;", {"email": payload.email})
    if rows:
        raise HTTPException(status_code=400, detail="Email already registered.")

    salt = secrets.token_hex(16)
    pwd_hash = hash_password(payload.password, salt)

    db_exec(
        """
        INSERT INTO users (email, password_hash, salt)
        VALUES (:email, :password_hash, :salt);
        """,
        {"email": payload.email, "password_hash": pwd_hash, "salt": salt},
    )

    return {"ok": True, "message": "Account created."}


@app.post("/login", tags=["auth"])
def login(payload: LoginIn):
    rows = db_exec(
        "SELECT id, password_hash, salt FROM users WHERE email = :email;",
        {"email": payload.email},
    )
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user = rows[0]
    check_hash = hash_password(payload.password, user["salt"])
    if check_hash != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # For simplicity return a pretend token (do NOT do this in production).
    # If you already have JWT in your project, replace this with your real token.
    token = secrets.token_urlsafe(24)
    return {"ok": True, "token": token}


@app.get("/jobs", response_model=List[JobOut], tags=["jobs"])
def list_jobs(q: Optional[str] = None, limit: int = 50):
    """
    Reads from a 'jobs' table if it exists with columns:
      id, title, company, location, url, posted_at
    If it doesn't exist, returns an empty list (no error).
    """
    if engine is None:
        # API still works without DB; just return empty list
        return []

    # Detect if jobs table exists
    exists = db_exec(
        """
        SELECT to_regclass('public.jobs') AS tbl;
        """
    )
    if not exists or not exists[0].get("tbl"):
        return []

    base_sql = """
        SELECT id, title, company, location, url, posted_at
        FROM jobs
    """
    params: Dict[str, Any] = {}
    where_parts = []

    if q:
        where_parts.append("(title ILIKE :q OR company ILIKE :q OR location ILIKE :q)")
        params["q"] = f"%{q}%"

    if where_parts:
        base_sql += " WHERE " + " AND ".join(where_parts)

    base_sql += " ORDER BY posted_at DESC NULLS LAST, id DESC LIMIT :limit;"
    params["limit"] = max(1, min(limit, 200))

    try:
        rows = db_exec(base_sql, params)
        return rows  # pydantic will coerce to JobOut list
    except Exception:
        # If query fails for any reason, don't kill the endpoint—just return empty.
        return []


# ------------------------------------------------------------------------------
# Uvicorn entrypoint (Render uses your start command; this is for local runs)
# ------------------------------------------------------------------------------
if _name_ == "_main_":
    # Local dev only:
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
>>>>>>> 5d2161f (Fix CORS, add full API with signup, login, jobs endpoints)



















































    
















