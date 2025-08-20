import { listJobs, applyJob } from './api.js';
const user = Session.get();
if(!user){ location.href = 'login.html'; }
const listEl = document.getElementById('jobsList');
const filters = document.getElementById('filters');
async function loadJobs(){
  const fd = new FormData(filters);
  const params = {
    country: fd.get('country') || undefined,
    company: fd.get('company') || undefined,
    min_score: fd.get('min_score') || undefined,
    limit: 50
  };
  try{
    const jobs = await listJobs(params);
    listEl.innerHTML = (jobs||[]).map(j=>`
      <div class="col-md-6 col-lg-4">
        <div class="card h-100 p-3">
          <div class="d-flex justify-content-between">
            <h5 class="fw-bold">${j.title}</h5>
            <span class="badge bg-success-subtle text-success-emphasis">Score ${j.match_score ?? '—'}</span>
          </div>
          <div class="text-muted small mb-2">${j.company} · ${j.location ?? ''}</div>
          <div class="small text-muted">Posted: ${j.post_advertised_date ?? '—'} · Closes: ${j.closing_date ?? '—'}</div>
          <div class="d-grid mt-3">
            <button class="btn btn-success apply-btn" data-id="${j.job_id}">Apply</button>
          </div>
        </div>
      </div>
    `).join('');
  }catch(err){
    listEl.innerHTML = `<div class="alert alert-danger">Failed to load jobs: ${err.message}</div>`;
  }
}
filters?.addEventListener('submit', (e)=>{ e.preventDefault(); loadJobs(); });
document.addEventListener('click', async (e)=>{
  const btn = e.target.closest('.apply-btn');
  if(!btn) return;
  try{
    const r = await applyJob(user.id, btn.dataset.id, 'Applied from AutoApply');
    alert('Application submitted: ' + r.status);
  }catch(err){ alert('Apply failed: ' + err.message); }
});
loadJobs();
