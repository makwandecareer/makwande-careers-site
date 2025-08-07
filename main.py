from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB Setup
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
users_collection = db["users"]

# OpenAI Setup
openai.api_key = OPENAI_API_KEY

# FastAPI App
app = FastAPI()

# CORS Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Auto Apply API is running!"}

@app.post("/signup")
async def signup(user: dict):
    if users_collection.find_one({"email": user["email"]}):
        raise HTTPException(status_code=400, detail="User already exists.")
    users_collection.insert_one(user)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: dict):
    db_user = users_collection.find_one({"email": user["email"], "password": user["password"]})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@app.post("/revamp-cv")
async def revamp_cv(request: Request):
    body = await request.json()
    cv_text = body.get("cv_text")
    if not cv_text:
        raise HTTPException(status_code=400, detail="CV text is required.")

    prompt = f"Revamp this CV for ATS compliance and improve structure:\n\n{cv_text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional CV revamper."},
                {"role": "user", "content": prompt}
            ]
        )
        revamped_cv = response["choices"][0]["message"]["content"]
        return {"revamped_cv": revamped_cv}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))












































    
















