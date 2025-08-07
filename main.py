from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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
def home():
    return {"message": "Welcome to AutoApply API"}

@app.get("/status")
def status_check():
    return {"status": "API is up and running"}

# MongoDB Example
from pymongo import MongoClient

MONGODB_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGODB_URL)
db = client["autoapply"]

@app.get("/users")
def get_users():
    users = list(db.users.find({}, {"_id": 0}))
    return {"users": users}












































    
















