from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from revamp_cv import revamp_router
from cover_letter import cover_router
from job_matcher import match_router
from tracking import tracking_router
from scrape_jobs import scraper_router
from subscription import router as subscription_router  # Paystack verification route

app = FastAPI()

# CORS for frontend connection
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://autoapplyapp.vercel.app",
    "https://autoapply.makwandecareers.co.za"  # optional future custom domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API health check
@app.get("/")
def read_root():
    return {"message": "AutoApply API is running"}

# Include all routers
app.include_router(revamp_router)
app.include_router(cover_router)
app.include_router(match_router)
app.include_router(tracking_router)
app.include_router(scraper_router)
app.include_router(subscription_router)

















    
















