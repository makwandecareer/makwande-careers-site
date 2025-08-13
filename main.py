# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
import hashlib
import os

# --------------------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "43200"))  # 30 days

# Shown in /api/health
API_VERSION = (
    os.getenv("API_VERSION")
    or os.getenv("RENDER_GIT_COMMIT", "")[:7]
    or "1.0.0"
)

ALLOWED_ORIGINS = [
    "https://autoapplyapp-mobile.onrender.com",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
# Allow override from env (comma separated)
if os.getenv("ALLOWED_ORIGINS"):
    ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS").split(",") if o.strip()]

# --------------------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------------------
app = FastAPI(title="AutoApply API", version=API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
)

security = HTTPBearer(auto_error=False)

# --------------------------------------------------------------------------------------
# Simple in-memory store (keeps your existing flows working; swap for DB when ready)
# --------------------------------------------------------------------------------------
_users: Dict[str, Dict] = {}   # key: email -> {id, name, email, password_hash}
_next_id = 1

def _hash_password(raw: str) -> str:
    return hashlib.sha256((SECRET_KEY + "::" + raw).encode("utf-8")).hexdigest()

def _create_token(payload: dict, minutes: int = ACCESS_TOKEN_MINUTES) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    to_encode.update({"iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=minutes)).timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def _decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# --------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------
class SignupBody(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginBody(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# --------------------------------------------------------------------------------------
# Auth helper
# --------------------------------------------------------------------------------------
def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not creds or not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        data = _decode_token(creds.credentials)
        email = data.get("sub")
        if not email or email not in _users:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return _users[email]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# --------------------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------------------
@app.get("/api/health")
def api_health():
    return {"status": "ok", "version": API_VERSION}

@app.get("/health")
def root_health():
    return {"status": "ok", "version": API_VERSION}

# --------------------------------------------------------------------------------------
# Auth: Signup + Login  (both /api/auth/* and /api/* aliases)
# --------------------------------------------------------------------------------------
def _signup(body: SignupBody) -> TokenResponse:
    global _next_id
    email = body.email.lower().strip()
    if email in _users:
        raise HTTPException(status_code=400, detail="User already exists")
    _users[email] = {
        "id": _next_id,
        "name": body.name.strip(),
        "email": email,
        "password_hash": _hash_password(body.password),
    }
    _next_id += 1
    token = _create_token({"sub": email, "name": _users[email]["name"], "uid": _users[email]["id"]})
    return TokenResponse(access_token=token, user={"id": _users[email]["id"], "name": _users[email]["name"], "email": email})

def _login(body: LoginBody) -> TokenResponse:
    email = body.email.lower().strip()
    user = _users.get(email)
    if not user or user["password_hash"] != _hash_password(body.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _create_token({"sub": email, "name": user["name"], "uid": user["id"]})
    return TokenResponse(access_token=token, user={"id": user["id"], "name": user["name"], "email": email})

# Primary paths
@app.post("/api/auth/signup", response_model=TokenResponse)
def signup_auth(body: SignupBody): return _signup(body)

@app.post("/api/auth/login", response_model=TokenResponse)
def login_auth(body: LoginBody): return _login(body)

# Compatible aliases (so 404s disappear if your frontend uses the shorter paths)
@app.post("/api/signup", response_model=TokenResponse)
def signup_alias(body: SignupBody): return _signup(body)

@app.post("/api/login", response_model=TokenResponse)
def login_alias(body: LoginBody): return _login(body)

# --------------------------------------------------------------------------------------
# Me (protected)
# --------------------------------------------------------------------------------------
@app.get("/api/me")
def me(user=Depends(get_current_user)):
    return {"id": user["id"], "name": user["name"], "email": user["email"]}

# --------------------------------------------------------------------------------------
# Misc convenience
# --------------------------------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "AutoApply API", "version": API_VERSION}

# Standard entrypoint (!!! make sure it’s __name__ == '__main__' !!!)
if __name__ == "__main__":
    # Local dev: python main.py
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

# --- canonical models/handlers (already in your file) ---
from pydantic import BaseModel

class LoginBody(BaseModel):
    email: str
    password: str

class SignupBody(BaseModel):
    name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/api/login", response_model=TokenResponse)
async def login(body: LoginBody):
    # ... your existing logic ...
    ...

@app.post("/api/signup", response_model=TokenResponse)
async def signup(body: SignupBody):
    # ... your existing logic ...
    ...

# --- add these tiny alias routes (fixes 404 immediately) ---
@app.post("/api/auth/login", response_model=TokenResponse)
async def login_alias(body: LoginBody):
    return await login(body)

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup_alias(body: SignupBody):
    return await signup(body)
