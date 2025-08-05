from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.subscription import router as subscription_router

app = FastAPI(
    title="AutoApplyApp API",
    description="Backend API for AutoApplyApp - AI-powered job application system",
    version="1.0.0"
)

# Allow CORS from frontend
origins = [
    "http://localhost:3000",
    "https://autoapplyapp.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to AutoApplyApp API!"}

# Register all routers
app.include_router(subscription_router, prefix="/api", tags=["Subscription"])

















    
















