# main.py
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime
from typing import Optional, List

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column, DateTime, Integer, String, UniqueConstraint, create_engine, text
)
from sqlalchemy.exc import NoSuchModuleError, OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
app = FastAPI(title="autoapply-api", version="1.0.0")

# ---- CORS (configure with ALLOW_ORIGINS env; comma-separated)
DEFAULT_ORIGIN = "https://autoapplyapp-mobile.onrender.com"  # your static site
origins_str = os.getenv("ALLOW_ORIGINS", DEFAULT_ORIGIN).strip()

if origins_str and origins_str != "DISABLED":
    if origins_str == "*":
        allow_origins: List[str] = ["*"]
    else:
        allow_origins = [o.strip() for o in origins_str.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

# Root + HEAD for load balancer probes
@app.get("/", include_in_schema=False)
async def root():
    return {"ok": True, "service": "autoapply-api"}

@app.head("/", include_in_schema=False)
async def root_head():
    return Response(status_code=200)

@app.get("/health", include_in_schema=False)
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception:
        return {"status": "ok", "db": "degraded"}

# -----------------------------------------------------------------------------
# DB (Postgres via DATABASE_URL; fallback to SQLite if unavailable)
# -----------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./autoapply.db")

def _make_engine(url: str):
    try:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return create_engine(url, pool_pre_ping=True, future=True)
    except NoSuchModuleError:
        return create_engine("sqlite:///./autoapply.db", pool_pre_ping=True, future=True)

engine = _make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_salt = Column(String(64), nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

try:
    Base.metadata.create_all(bind=engine)
except OperationalError:
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Password hashing (salted SHA256)
# -----------------------------------------------------------------------------
def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return salt, digest

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    _, digest = hash_password(password, salt)
    return hmac.compare_digest(digest, expected_hash)

# -----------------------------------------------------------------------------
# Minimal HMAC token (dependency-free)
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_super_secret_key")
TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", "604800"))  # 7 days

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _b64url_to_bytes(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def create_token(user_id: int, email: str, ttl: int = TOKEN_TTL_SECONDS) -> str:
    payload = {"sub": user_id, "email": email, "exp": int(time.time()) + ttl}
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
    return f"{payload_b64}.{_b64url(sig)}"

def verify_token(token: str) -> Optional[dict]:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        expected = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_to_bytes(sig_b64)):
            return None
        payload = json.loads(_b64url_to_bytes(payload_b64))
        if int(time.time()) > int(payload.get("exp", 0)):
            return None
        return payload
    except Exception:
        return None

# -----------------------------------------------------------------------------
# Schemas & auth dependency
# -----------------------------------------------------------------------------
class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class AuthOut(BaseModel):
    token: str
    user: dict

def current_user(
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not Authorization or not Authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = Authorization.split(" ", 1)[1].strip()
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.post("/auth/signup", response_model=AuthOut)
def signup(body: SignupIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    salt, digest = hash_password(body.password)
    user = User(
        name=body.name.strip(),
        email=body.email.lower(),
        password_salt=salt,
        password_hash=digest,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.email)
    return {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.post("/auth/login", response_model=AuthOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_salt, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user.id, user.email)
    return {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "created_at": user.created_at.isoformat()}

# -----------------------------------------------------------------------------
# Local dev
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=True)
