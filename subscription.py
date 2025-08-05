from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import requests
import os

router = APIRouter()

# Load Paystack secret key from environment variable
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"

# Pydantic model for request body
class SubscriptionRequest(BaseModel):
    email: str
    plan_code: str # Your Paystack plan code (e.g., PLN_xxx)
    callback_url: str

@router.post("/subscribe")
def create_subscription(data: SubscriptionRequest):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": data.email,
        "plan": data.plan_code,
        "callback_url": data.callback_url
    }

    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="Subscription initiation failed")


@router.get("/verify/{reference}")
def verify_payment(reference: str):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail="Verification failed")