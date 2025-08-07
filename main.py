from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import hashlib

app = FastAPI()

# CORS config (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set your Vercel frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory DB (use SQLite/PostgreSQL in production)
users_db: Dict[str, str] = {}

class User(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/signup")
def signup(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered.")
    users_db[user.email] = hash_password(user.password)
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: User):
    if user.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if users_db[user.email] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful"}













































    
















