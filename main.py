from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os, sqlite3, json, hmac, hashlib, jwt
from passlib.hash import bcrypt

API_VERSION = "v1.0.0"
app = FastAPI(title="AutoApply API", version=API_VERSION)

# ===== AUTH (JWT + SQLite) =====
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-prod")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

db = sqlite3.connect("app.db", check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
)
""")
db.commit()

def _user_row_to_dict(r):
    return {"id": r[0], "email": r[1], "name": r[2], "password_hash": r[3], "created_at": r[4]}

def get_user_by_email(email: str):
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    r = cur.fetchone()
    return _user_row_to_dict(r) if r else None

def create_user(email: str, name: str, password: str):
    ph = bcrypt.hash(password)
    now = datetime.utcnow().isoformat()
    cur = db.cursor()
    cur.execute("INSERT INTO users(email,name,password_hash,created_at) VALUES(?,?,?,?)",
                (email.strip().lower(), name.strip(), ph, now))
    db.commit()
    return {"id": cur.lastrowid, "email": email.strip().lower(), "name": name.strip(), "created_at": now}

def verify_user(email: str, password: str):
    u = get_user_by_email(email)
    if not u or not bcrypt.verify(password, u["password_hash"]):
        return None
    return u

def make_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
        "iss": "autoapply-api"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def require_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

class SignupBody(BaseModel):
    email: str
    name: str
    password: str

class LoginBody(BaseModel):
    email: str
    password: str

# ===== HEALTH (and /api alias for proxy) =====
@app.get("/health")
def health():
    return {"status": "ok", "service": "autoapply-api", "version": API_VERSION}

@app.get("/api/health")
def api_health():
    return health()

# ===== AUTH ROUTES =====
@app.post("/api/auth/signup")
def auth_signup(body: SignupBody):
    if get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    u = create_user(body.email, body.name, body.password)
    token = make_token(u["id"])
    return {"access_token": token, "token_type": "bearer",
            "user": {"id": u["id"], "email": u["email"], "name": u["name"]}}

@app.post("/api/auth/login")
def auth_login(body: LoginBody):
    u = verify_user(body.email, body.password)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(u["id"])
    return {"access_token": token, "token_type": "bearer",
            "user": {"id": u["id"], "email": u["email"], "name": u["name"]}}

@app.get("/api/me")
def me(user_id: int = Depends(require_user)):
    cur = db.cursor()
    cur.execute("SELECT id,email,name,created_at FROM users WHERE id = ?", (user_id,))
    r = cur.fetchone()
    if not r: raise HTTPException(status_code=404, detail="User not found")
    return {"id": r[0], "email": r[1], "name": r[2], "created_at": r[3]}

# ===== JOBS + APPLY =====
class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    match_score: float
    post_advertised_date: Optional[str] = None
    closing_date: Optional[str] = None

MOCK_JOBS: List[Job] = [
    Job(id="J001", title="Process Engineer", company="ChemWorks SA", location="Gauteng",
        match_score=0.87, post_advertised_date="2025-08-01", closing_date="2025-08-20"),
    Job(id="J002", title="Data Analyst", company="Insight Hub", location="Western Cape",
        match_score=0.79, post_advertised_date="2025-08-05", closing_date="2025-08-25"),
]

@app.get("/api/jobs", response_model=List[Job])
def list_jobs(location: Optional[str] = None, company: Optional[str] = None, min_score: Optional[float] = None):
    jobs = MOCK_JOBS
    if location: jobs = [j for j in jobs if j.location.lower() == location.lower()]
    if company: jobs = [j for j in jobs if j.company.lower() == company.lower()]
    if min_score is not None: jobs = [j for j in jobs if j.match_score >= min_score]
    return jobs

@app.post("/api/apply_job")
async def apply_job(job_id: str = Form(...), cv: UploadFile = File(...), full_name: str = Form("AutoApply User")):
    _ = await cv.read()
    return {"ok": True, "application_id": f"APP-{job_id}-12345"}

# ===== REVAMP (stub) =====
class RevampRequest(BaseModel):
    cv_text: str
    job_spec: Optional[str] = None

@app.post("/api/revamp")
def revamp(req: RevampRequest):
    suggestions = [
        "Add quantifiable achievements under recent roles.",
        "Include relevant keywords from the job spec in skills section.",
        "Reorder experience to highlight domain alignment.",
    ]
    return {"ats_score": 85.0, "match_rate": 82.0,
            "suggestions": suggestions, "revamped_cv": "(ATS-optimized CV content here.)"}

# ===== PAYSTACK WEBHOOK (optional stub) =====
def _paystack_signature_valid(body: bytes, signature: str) -> bool:
    secret = os.getenv("PAYSTACK_SECRET_KEY", "")
    if not secret or not signature: return False
    mac = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha512).hexdigest()
    return hmac.compare_digest(mac, signature)

@app.post("/api/paystack/webhook")
async def paystack_webhook(request: Request, x_paystack_signature: Optional[str] = Header(None)):
    raw = await request.body()
    if not _paystack_signature_valid(raw, x_paystack_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    event = json.loads(raw.decode("utf-8"))
    return {"received": True, "event": event.get("event")}

@app.get("/api/applications/protected")
def applications_protected(user_id: int = Depends(require_user)):
    return {"user_id": user_id, "applications": [{"id": "APP-1", "status": "submitted"}]}
























































    
















