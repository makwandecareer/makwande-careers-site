from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URL"))
db = client["autoapply"]
users_collection = db["users"]

# Request body models
class User(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/signup")
async def signup(user: User):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_collection.insert_one(user.dict())
    return {"message": "Account created successfully!"}

@app.post("/login")
async def login(login: LoginRequest):
    user = users_collection.find_one({"email": login.email})
    if not user or user["password"] != login.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"message": "Login successful!"}










































    
















