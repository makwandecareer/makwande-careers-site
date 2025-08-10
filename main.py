# main.py
from datetime import datetime, timedelta, timezone
import os
from typingfrom fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Auto Apply API",
    description="Backend API for Auto Apply App",
    version="1.0.0",
    docs_url="/docs",          # Ensure this is set
    redoc_url="/redoc"         # Optional
)

origins = [
    "https://autoapplyapp-mobile.onrender.com",
    # Add other frontend URLs if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}



















































    
















