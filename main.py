from fastapi import FastAPI
import snowflake.connector
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AutoApplyApp FastAPI is live!"}

@app.get("/test-connection")
def test_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_VERSION()")
        version = cur.fetchone()[0]
        return {"status": "connected", "snowflake_version": version}
    except Exception as e:
        return {"status": "error", "details": str(e)}








