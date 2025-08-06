from fastapi import FastAPI, Request
import snowflake.connector
from datetime import datetime, timedelta
import os
import requests

app = FastAPI()

# Paystack Test Secret Key (Replace with LIVE key when launching)
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_xxxxxxxxxxxxxxxxx")

# Snowflake connection
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

# ✅ Paystack Payment Verification Endpoint
@app.post("/api/verify_payment")
async def verify_payment(request: Request):
    data = await request.json()
    reference = data.get("reference")
    user_email = data.get("email")

    if not reference or not user_email:
        return {"status": "error", "message": "Missing payment reference or email"}

    # Verify payment with Paystack
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    result = response.json()

    if result["status"] and result["data"]["status"] == "success":
        # ✅ Payment is successful → Update subscription in Snowflake
        expiry_date = datetime.now() + timedelta(days=30)

        conn = get_snowflake_connection()
        cur = conn.cursor()

        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SUBSCRIPTIONS (
                user_email STRING,
                status STRING,
                expiry_date DATE
            )
        """)

        # Upsert subscription record
        cur.execute(f"""
            MERGE INTO SUBSCRIPTIONS t
            USING (SELECT '{user_email}' AS user_email, 'Active' AS status, '{expiry_date.strftime('%Y-%m-%d')}' AS expiry_date) s
            ON t.user_email = s.user_email
            WHEN MATCHED THEN
              UPDATE SET status = s.status, expiry_date = s.expiry_date
            WHEN NOT MATCHED THEN
              INSERT (user_email, status, expiry_date)
              VALUES (s.user_email, s.status, s.expiry_date)
        """)

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Payment verified and subscription updated",
            "expiry_date": expiry_date.strftime("%Y-%m-%d")
        }
    else:
        return {"status": "error", "message": "Payment verification failed"}









































    
















