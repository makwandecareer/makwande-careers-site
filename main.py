from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import jobs  # make sure you have __init__.py in routes folder

app = FastAPI()

# CORS setup to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def read_root():
    return {"message": "AutoApply API is live"}

# Register routes
app.include_router(jobs.router, prefix="/api")























    
















