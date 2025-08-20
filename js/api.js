// Auth
export async function signup(username,email,password){
  return fetchJSON(`${API_BASE}/api/signup`, {method:'POST', body:JSON.stringify({username,email,password})});
}
export async function login(email,password){
  return fetchJSON(`${API_BASE}/api/login`, {method:'POST', body:JSON.stringify({email,password})});
}
// Jobs
export async function listJobs(params={}){
  const q = new URLSearchParams(Object.entries(params).filter(([,v])=>v!==undefined && v!==''));
  return fetchJSON(`${API_BASE}/api/jobs?${q.toString()}`);
}
export async function applyJob(user_id, job_id, notes=''){
  return fetchJSON(`${API_BASE}/api/apply_job`, {method:'POST', body:JSON.stringify({user_id,job_id,notes})});
}
export async function getApplications(user_id){
  return fetchJSON(`${API_BASE}/api/applications/${user_id}`);
}
// AI
export async function revampCV(resume_text, job_description=''){
  return fetchJSON(`${API_BASE}/api/ai/revamp_cv`, {method:'POST', body:JSON.stringify({resume_text,job_description})});
}
export async function coverLetter(resume_text, job_title, company, job_description=''){
  return fetchJSON(`${API_BASE}/api/ai/cover_letter`, {method:'POST', body:JSON.stringify({resume_text,job_title,company,job_description})});
}
export async function atsScore(resume_text, job_description){
  return fetchJSON(`${API_BASE}/api/ai/ats_score`, {method:'POST', body:JSON.stringify({resume_text,job_description})});
}
export async function matchExplain(resume_text, job_description){
  return fetchJSON(`${API_BASE}/api/ai/match_explain`, {method:'POST', body:JSON.stringify({resume_text,job_description})});
}
// Payments
export async function verifyPaystack(reference, user_id){
  return fetchJSON(`${API_BASE}/api/payment/verify`, {method:'POST', body:JSON.stringify({reference,user_id})});
}
// Recruiter / Employer (backend must supply these endpoints)
export async function recruiterPost(payload){
  return fetchJSON(`${API_BASE}/api/recruiter/post`, {method:'POST', body:JSON.stringify(payload)});
}
export async function employerRegister(payload){
  return fetchJSON(`${API_BASE}/api/employer/register`, {method:'POST', body:JSON.stringify(payload)});
}
