from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os

router = APIRouter()

openai.api_key = os.getenv("OPENAI_API_KEY")

class CVRevampRequest(BaseModel):
    cv_text: str
    job_description: str
    user_level: str  # "graduate", "mid-level", "senior"

@router.post("/api/revamp_cv")
async def revamp_cv(data: CVRevampRequest):
    prompt = f"""
You are a world-class HR and ATS-compliant CV expert.

Your task:
- Revamp the following CV to match the job description
- Make sure the CV passes ATS systems (like Lever, Greenhouse, Workday, etc.)
- Adapt tone and structure to the user's level: {data.user_level}
- Format clearly with no graphics, columns, or tables
- Ensure measurable results and use keywords from job description

Job Description:
{data.job_description}

Original CV:
{data.cv_text}

Please return the improved, full CV:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1800,
        temperature=0.7,
    )
    return {"revamped_cv": response['choices'][0]['message']['content']}
