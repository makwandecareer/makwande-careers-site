import openai

openai.api_key = "your_openai_api_key_here"  # Use env variable in production

def generate_cover_letter(name, job_title, company, job_description, user_cv):
    prompt = f"""
You are an expert career coach and resume writer. Write a highly personalized and ATS-compliant cover letter based on the following:
- Candidate Name: {name}
- Target Job Title: {job_title}
- Target Company: {company}
- Job Description: {job_description}
- Candidate CV Content: {user_cv}

Your goal is to:
- Highlight the candidate’s relevant experience
- Use deep reasoning to align their strengths with the job
- Match tone to the industry (formal, persuasive, tech-savvy, etc.)
- Ensure it is 100% ATS-friendly (no graphics, tables, headers, or fancy formatting)
- Keep it concise and powerful (max 400 words)

Begin now:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
