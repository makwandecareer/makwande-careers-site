import os
import sys
import logging
import traceback
from typing import Generator

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext

# --------------------------
# Logging
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("autoapply-api")

# --------------------------
# Environment / DB URL
# --------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Normalize scheme for SQLAlchemy/psycopg2
# Accept postgres://, postgresql:// -> convert to postgresql+psycopg2://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

if not DATABASE_URL:
    log.error("FATAL: DATABASE_URL not set")
    raise RuntimeError("DATABASE_URL not set")

# --------------------------
# SQLAlchemy setup
# --------------------------
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # drops dead connections
        future=True,
    )
    log.info("Engine created successfully")
except Exception as e:
    log.error("FATAL: create_engine failed: %s", e)
    traceback.print_exc()
    raise

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# --------------------------
# Password hashing
# --------------------------
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_ctx.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd_ctx.verify(p, h)

# --------------------------
# Models
# --------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

# --------------------------
# Pydantic Schemas
# --------------------------
class SignupBody(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginBody(BaseModel):
    email: EmailStr
    password: str

class Message(BaseModel):
    message: str

# --------------------------
# FastAPI app
# --------------------------
app = FastAPI(title="AutoApply API", version="1.0.0")

# CORS: keep wide open during bring-up. Later, set your exact domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # e.g. ["https://autoapply.makwandecareer.co.za"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# DB Dependency
# --------------------------
def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# --------------------------
# Startup: create tables
# --------------------------
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        log.info("DB tables ensured/created")
        # quick ping
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("DB connectivity OK")
    except Exception as e:
        log.error("Startup DB check failed: %s", e)
        traceback.print_exc()
        # re-raise to fail fast (Render will show the traceback)
        raise

# --------------------------
# Health
# --------------------------
@app.get("/health", response_model=Message)
def health() -> Message:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"message": "ok"}
    except Exception as e:
        log.error("Health DB check failed: %s", e)
        raise HTTPException(status_code=500, detail="db_unreachable")

# --------------------------
# Auth: Signup & Login
# NOTE: Using /api prefix to match your frontend calls (/api/signup, /api/login)
# --------------------------
@app.post("/api/signup", response_model=Message)
def signup(body: SignupBody, db: Session = Depends(get_db)) -> Message:
    email = body.email.lower().strip()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=body.full_name.strip(),
        email=email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    return {"message": "Signup successful"}

@app.post("/api/login", response_model=Message)
def login(body: LoginBody, db: Session = Depends(get_db)) -> Message:
    email = body.email.lower().strip()
    u = db.query(User).filter(User.email == email).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": f"Welcome back, {u.full_name}!"}

















































    
















