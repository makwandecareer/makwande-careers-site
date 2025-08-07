from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Allow CORS for frontend (you can restrict this to your Netlify domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["https://your-netlify-site.netlify.app"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory user store (replace with DB later)
users_db = {}

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

@app.post("/api/signup")
async def signup(request: SignupRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    users_db[request.email] = {
        "name": request.name,
        "password": request.password  # In production, hash this!
    }
    return {"message": "User registered successfully"}










































    
















