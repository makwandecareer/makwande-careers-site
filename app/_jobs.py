# app/_jobs.py

import snowflake.connector
import os

def fetch_jobs_from_snowflake():
    """
    Connects to the Snowflake database and retrieves matched job listings
    from the MATCHED_JOBS table. Returns a list of job dictionaries or an error.
    """
    try:
        # Snowflake connection using environment variables for security
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )

        cursor = conn.cursor()
        # Fetch the 10 most recent jobs
        cursor.execute("SELECT * FROM MATCHED_JOBS ORDER BY POST_ADVERTISED_DATE DESC LIMIT 10;")
        rows = cursor.fetchall()

        # Get column names
        columns = [col[0] for col in cursor.description]
        # Combine column names and values into dictionaries
        jobs = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return jobs

    except Exception as e:
        return {"error": str(e)}
