from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import hashlib, uuid, time

app = FastAPI(title="AutoApply API", version="1.0.0")

# --- CORS (allow your static site and dev) -----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # relax for now; tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory stores (simple & deployment-safe; replace with DB later) ------
USERS: Dict[str, Dict[str, Any]] = {}      # email -> user dict
TOKENS: Dict[str, str] = {}                # token -> email
APPLICATIONS: Dict[str, List[Dict[str, Any]]] = {}  # email -> list
JOBS: List[Dict[str, Any]] = [
    {"id": "J101", "title": "Junior Data Analyst", "company": "Acme", "url": "https://example.com/jobs/101"},
    {"id": "J202", "title": "Software Engineer",  "company": "Globex","url": "https://example.com/jobs/202"},
    {"id": "J303", "title": "Support Specialist", "company": "Initech","url": "https://example.com/jobs/303"},
]

# --- Helpers -----------------------------------------------------------------
def _hash_pw(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _new_token() -> str:
    return uuid.uuid4().hex

def _require_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1].strip()
    email = TOKENS.get(token)
    if not email or email not in USERS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return USERS[email]

# --- Schemas -----------------------------------------------------------------
class SignupBody(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginBody(BaseModel):
    email: EmailStr
    password: str

class RevampRequest(BaseModel):
    text: str

class ApplyJobBody(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None

# --- Health ------------------------------------------------------------------
@app.get("/health")
def health_root():
    return {"ok": True, "service": "autoapply-api"}

@app.get("/api/health")
def health_api():
    return {"ok": True, "service": "autoapply-api", "version": app.version}

# --- Auth --------------------------------------------------------------------
@app.post("/api/auth/signup")
def signup(body: SignupBody):
    email = body.email.lower()
    if email in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    user = {
        "id": len(USERS) + 1,
        "name": body.name.strip(),
        "email": email,
        "password_hash": _hash_pw(body.password),
        "created_at": int(time.time()),
    }
    USERS[email] = user
    token = _new_token()
    TOKENS[token] = email
    # response payload matches typical JWT style field names used by UIs
    return {"access_token": token, "token_type": "bearer", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

@app.post("/api/auth/login")
def login(body: LoginBody):
    email = body.email.lower()
    user = USERS.get(email)
    if not user or user["password_hash"] != _hash_pw(body.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _new_token()
    TOKENS[token] = email
    return {"access_token": token, "token_type": "bearer", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

@app.get("/api/me")
def me(current=Depends(_require_user)):
    return {"id": current["id"], "name": current["name"], "email": current["email"]}

# --- Jobs --------------------------------------------------------------------
@app.get("/api/jobs")
def list_jobs() -> List[Dict[str, Any]]:
    return JOBS

@app.post("/api/apply_job")
def apply_job(body: ApplyJobBody, current=Depends(_require_user)):
    # pretend to apply & save application
    entry = {"when": int(time.time()), "job_id": body.id, "url": body.url, "notes": body.notes}
    APPLICATIONS.setdefault(current["email"], []).append(entry)
    return {"applied": True, "entry": entry}

@app.get("/api/applications/protected")
def list_my_applications(current=Depends(_require_user)):
    return {"items": APPLICATIONS.get(current["email"], [])}

# --- CV Revamp (stub) --------------------------------------------------------
@app.post("/api/revamp")
def revamp(body: RevampRequest, current=Depends(_require_user)):
    # very simple demo transformer
    cleaned = " ".join(body.text.split())
    improved = cleaned.capitalize()
    return {"input_len": len(body.text), "output": improved}

# --- Paystack webhook (no-op stub) -------------------------------------------
@app.post("/api/paystack/webhook")
async def paystack_webhook(request: Request):
    _ = await request.body()
    return {"received": True}