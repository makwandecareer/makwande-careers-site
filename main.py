from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoApply API", version="1.0.0")

# --- CORS ---
ALLOWED_ORIGINS = [
    "https://autoapplyapp-mobile.onrender.com",  # your static site
    "http://localhost:5500",                     # optional for local testing
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "autoapply-api"}

@app.get("/health")
def health():
    return {"ok": True}

# Demo endpoints you can call from the static site later
@app.get("/api/jobs")
def jobs():
    return [
        {"id": 1, "title": "Software Engineer", "company": "Acme"},
        {"id": 2, "title": "Data Analyst", "company": "Globex"},
    ]



















































    
















