from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# ===============================
# CONFIGURATION
# ===============================
# Load Paystack Test Secret Key from environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_xxxxxxxxxxxxxxxxxxxxxx")

# Serve static Bootstrap HTML files from /frontend folder
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# ===============================
# DATA MODELS
# ===============================
class PaymentVerify(BaseModel):
    reference: str

class DetailRequest(BaseModel):
    candidate_id: str
    recruiter_id: str

class DetailResponse(BaseModel):
    request_id: str
    action: str  # "approve" or "decline"

# ===============================
# ROUTES
# ===============================
@app.get("/api")
def home():
    return {"message": "AutoApply Backend running in Test Mode with Bootstrap frontend"}

# Payment verification (Paystack Test Mode)
@app.post("/verify-payment")
def verify_payment(data: PaymentVerify):
    url = f"https://api.paystack.co/transaction/verify/{data.reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data.get("status") and res_data["data"]["status"] == "success":
        return {
            "status": "success",
            "reference": data.reference,
            "amount": res_data["data"]["amount"],
            "currency": res_data["data"]["currency"],
            "customer_email": res_data["data"]["customer"]["email"]
        }
    return {
        "status": "failed",
        "reference": data.reference,
        "message": res_data.get("message", "Verification failed")
    }

# Request candidate details
@app.post("/request-details")
def request_details(data: DetailRequest):
    return {"message": f"Request sent to candidate {data.candidate_id} for recruiter {data.recruiter_id}"}

# Candidate responds to request
@app.post("/respond-details")
def respond_details(data: DetailResponse):
    if data.action.lower() == "approve":
        return {"message": "You approved the request. Recruiter can now view your details."}
    elif data.action.lower() == "decline":
        return {"message": "You declined the request. Your details remain hidden."}
    return {"message": "Invalid action."}

# Get applicants list with approval status
@app.get("/get-applicants")
def get_applicants(recruiter_id: str):
    return [
        {"candidate_id": "123", "name": "John D.", "email": "john@example.com", "phone": "060-123-4567", "skills": "Python, Data Analysis", "status": "approved"},
        {"candidate_id": "124", "name": "Jane S.", "email": "jane@example.com", "phone": "060-987-6543", "skills": "Project Management, Agile", "status": "pending"},





































    
















