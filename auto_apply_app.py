import streamlit as st
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer, util

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

st.title("🤖 Auto Apply Job Matcher")
st.subheader("Upload your CV and find the best job matches!")

# Upload CV
uploaded_file = st.file_uploader("📄 Upload your CV (Text Format)", type=["txt"])
if uploaded_file is not None:
    cv_text = uploaded_file.read().decode("utf-8")
    cv_embedding = model.encode(cv_text, convert_to_tensor=True)

    # Fetch remote jobs
    with st.spinner("🔍 Fetching jobs..."):
        response = requests.get("https://remotive.io/api/remote-jobs")
        jobs_data = response.json().get("jobs", [])

        matched_jobs = []
        for job in jobs_data:
            job_title = job["title"]
            job_desc = job["description"]
            job_url = job["url"]
            combined = job_title + " " + job_desc

            job_embedding = model.encode(combined, convert_to_tensor=True)
            score = util.cos_sim(cv_embedding, job_embedding).item() * 100

            if score > 50:  # Threshold can be adjusted
                matched_jobs.append({
                    "Job Title": job_title,
                    "Company": job["company_name"],
                    "Match %": round(score, 2),
                    "Link": job_url
                })

        if matched_jobs:
            st.success(f"✅ Found {len(matched_jobs)} matching jobs!")
            df = pd.DataFrame(matched_jobs)
            df["Apply"] = df["Link"].apply(lambda x: f"[Apply Now]({x})")
            st.write(df[["Job Title", "Company", "Match %", "Apply"]], unsafe_allow_html=True)
        else:
            st.warning("⚠️ No matches found. Try improving your CV or uploading a different one.")
