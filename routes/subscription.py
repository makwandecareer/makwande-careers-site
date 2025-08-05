import os
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

@router.get("/verify-subscription/{reference}")
def verify_subscription(reference: str):
    if not PAYSTACK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Paystack secret key not set.")

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get("status") and data["data"]["status"] == "success":
        return {
            "status": "success",
            "email": data["data"]["customer"]["email"],
            "amount_paid": data["data"]["amount"] / 100,
            "plan": data["data"]["plan_object"]["name"],
            "reference": data["data"]["reference"]
        }

    raise HTTPException(status_code=400, detail=data.get("message", "Verification failed"))
