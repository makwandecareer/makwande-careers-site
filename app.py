import streamlit as st
import snowflake.connector
import pandas as pd

st.set_page_config(page_title="AutoApply Dashboard", layout="wide")
st.title("🚀 Makwande Careers – AutoApply Dashboard")

# Connect to Snowflake
@st.cache_resource
def get_data():
    conn = snowflake.connector.connect(
    user=st.secrets["user"],
    password=st.secrets["password"],
    account=st.secrets["account"],
    warehouse=st.secrets["warehouse"],
    database=st.secrets["database"],
    schema=st.secrets["schema"],
    role=st.secrets["role"]
)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MATCHED_JOBS")
    df = cursor.fetch_pandas_all()
    cursor.close()
    conn.close()
    return df

# Load data
df = get_data()

# Sidebar Filters
st.sidebar.header("🔍 Filter Jobs")
search = st.sidebar.text_input("Search job title or company")
min_score = st.sidebar.slider("Minimum Match Score", 0.0, 1.0, 0.7)

# Apply Filters
if search:
    df = df[df['JOB_TITLE'].str.contains(search, case=False) | df['COMPANY'].str.contains(search, case=False)]
df = df[df['MATCH_SCORE'] >= min_score]

# Display Table
st.write(f"### Showing {len(df)} matched jobs")
st.dataframe(df, use_container_width=True)

# Download CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Results as CSV",
    data=csv,
    file_name='filtered_matched_jobs.csv',
    mime='text/csv'
)

# Show Clickable Job Links
st.markdown("---")
st.subheader("📎 Clickable Job Links")
for _, row in df.iterrows():
    st.markdown(f"- [{row['JOB_TITLE']} at {row['COMPANY']}]({row['JOB_URL']}) — Match Score: **{row['MATCH_SCORE']}**")

