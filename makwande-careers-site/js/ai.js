import { revampCV, atsScore, coverLetter } from './api.js';

// Revamp page
const revampForm = document.getElementById('revampForm');
const revampOut = document.getElementById('revampOut');
const scoreOut = document.getElementById('scoreOut');
const scoreBtn = document.getElementById('scoreBtn');

revampForm?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(revampForm);
  try{
    const r = await revampCV(fd.get('resume_text'), fd.get('job_description')||'');
    revampOut.textContent = r.revamped_markdown || JSON.stringify(r,null,2);
  }catch(err){ revampOut.textContent = 'Error: ' + err.message; }
});

scoreBtn?.addEventListener('click', async ()=>{
  const fd = new FormData(revampForm);
  try{
    const r = await atsScore(fd.get('resume_text'), fd.get('job_description')||'');
    scoreOut.textContent = JSON.stringify(r, null, 2);
  }catch(err){ scoreOut.textContent = 'Error: ' + err.message; }
});

// Cover letter page
const coverForm = document.getElementById('coverForm');
const coverOut = document.getElementById('coverOut');

coverForm?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(coverForm);
  try{
    const r = await coverLetter(fd.get('resume_text'), fd.get('job_title'), fd.get('company'), fd.get('job_description')||'');
    coverOut.textContent = r.cover_letter || JSON.stringify(r,null,2);
  }catch(err){ coverOut.textContent = 'Error: ' + err.message; }
});
