import os
import streamlit as st
import snowflake.connector

# ✅ First, check for Render environment variables (cloud)
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", st.secrets.get("SNOWFLAKE_USER"))
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", st.secrets.get("SNOWFLAKE_PASSWORD"))
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", st.secrets.get("SNOWFLAKE_ACCOUNT"))
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", st.secrets.get("SNOWFLAKE_WAREHOUSE"))
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", st.secrets.get("SNOWFLAKE_DATABASE"))
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", st.secrets.get("SNOWFLAKE_SCHEMA"))
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE", st.secrets.get("SNOWFLAKE_ROLE"))

# ✅ Snowflake connection
conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA,
    role=SNOWFLAKE_ROLE
)

# ✅ Streamlit App Layout
st.title("🚀 Makwande Careers – AutoApply Dashboard")

query = "SELECT industry, job_title, location FROM MATCHED_JOBS LIMIT 20"
cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()
cursor.close()

st.subheader("Top Jobs from Snowflake")
for row in rows:
    st.write(f"**Industry:** {row[0]} | **Job Title:** {row[1]} | **Location:** {row[2]}")




