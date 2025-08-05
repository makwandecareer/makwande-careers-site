from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import snowflake.connector
import os

app = FastAPI()

# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Snowflake using environment variables
def connect_to_snowflake():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

@app.get("/")
def root():
    return {"message": "Auto Apply API is running!"}

@app.get("/api/test-connection")
def test_connection():
    try:
        conn = connect_to_snowflake()
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        result = cursor.fetchone()
        return {"status": "connected", "version": result[0]}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Add more endpoints here: /api/jobs, /api/revamp, etc.


















    
















