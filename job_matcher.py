from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import openai
import os

# Load your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

match_router = APIRouter()

class JobItem(BaseModel):
    job_title: str
    company: str
    location: str
    description: str

class MatchRequest(BaseModel):
    user_cv: str
    job_list: List[JobItem]

@match_router.post("/api/match_jobs")
async def match_jobs(payload: MatchRequest):
    try:
        cv = payload.user_cv
        jobs = payload.job_list

        # Get embedding of user CV
        cv_embed = get_embedding(cv)

        matches = []
        for job in jobs:
            job_embed = get_embedding(job.description)
            score = cosine_similarity(cv_embed, job_embed)
            reasoning = explain_match(cv, job.description)

            matches.append({
                "job_title": job.job_title,
                "company": job.company,
                "location": job.location,
                "match_score": round(score * 100, 2),
                "reasoning": reasoning
            })

        # Sort by best match
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return { "matches": matches }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def cosine_similarity(vec1, vec2):
    import numpy as np
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def explain_match(cv, job_desc):
    prompt = f"""
Compare the following candidate CV and job description, and explain if this is a good fit or not. Be honest, specific, and short.

CV:
{cv}

Job Description:
{job_desc}

Answer:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message['content'].strip()

