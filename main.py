from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import bcrypt

app = FastAPI()

# Allow frontend from Netlify
origins = [
    "https://autoapplyapp.netlify.app",  # Replace with actual Netlify domain
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority")
db = client["autoapply"]
users = db["users"]

class User(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

@app.post("/signup")
def signup(user: User):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_pw
    })
    return {"message": "Account created successfully!"}

@app.post("/login")
def login(data: LoginData):
    user = users.find_one({"email": data.email})
    if not user or not bcrypt.checkpw(data.password.encode('utf-8'), user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user": {
            "full_name": user["full_name"],
            "email": user["email"]
        }
    }










































    
















