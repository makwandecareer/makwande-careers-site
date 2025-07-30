import streamlit as st
import snowflake.connector

# Streamlit title
st.title("Makwande Careers – AutoApply Dashboard")

# Connect to Snowflake using secrets.toml
conn = snowflake.connector.connect(
    user=st.secrets["user"],
    password=st.secrets["password"],
    account=st.secrets["account"],
    warehouse=st.secrets["warehouse"],
    database=st.secrets["database"],
    schema=st.secrets["schema"],
    role=st.secrets["role"]
)

# Query jobs table
cursor = conn.cursor()
cursor.execute("SELECT industry, job_title, location FROM MATCHED_JOBS LIMIT 20")
rows = cursor.fetchall()

# Show results in Streamlit
st.subheader("Job Listings")
for row in rows:
    st.write(f"*{row[1]}* in {row[0]} — 📍 {row[2]}")

cursor.close()
conn.close()



