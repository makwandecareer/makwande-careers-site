from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.jobs import router as jobs_router
from routes.subscription import router as subscription_router

app = FastAPI()

# Allow access from your frontend domain (e.g. Vercel)
origins = [
    "https://your-frontend.vercel.app",  # replace with your actual frontend domain
    "http://localhost:3000",  # for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(subscription_router, prefix="/api/subscription", tags=["Subscription"])

@app.get("/")
def read_root():
    return {"message": "Auto Apply API is live."}























    
















