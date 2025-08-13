from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoApply API")

# CORS (allow the mobile site and localhost while testing)
ALLOWED = ["*"]  # you can restrict later
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# health checks (both paths just in case the frontend calls either)
@app.get("/health")
def health_root():
    return {"ok": True}

@app.get("/api/health")
def health_api():
    return {"status": "ok"}

# simple “me” endpoint to test auth wiring later
@app.get("/api/me")
def me():
    return {"email": "test@example.com", "name": "Test User"}

if _name_ == "_main_":
    import uvicorn, os
    port = int(os.getenv("PORT", "8080"))  # default 8080
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
