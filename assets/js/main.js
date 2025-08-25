
// Simple API helper using relative /api/* paths (same-origin via Render rewrite)
async function api(path, { method='GET', headers={}, body=null, form=false } = {}) {
  const opts = { method, headers: { ...headers }, credentials: 'include' };
  if (form) {
    opts.body = body; // FormData (no content-type)
  } else if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`/api${path}`, opts);
  if (!res.ok) {
    const t = await res.text().catch(()=>'');
    throw new Error(t || `Request failed: ${res.status}`);
  }
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return await res.json();
  return await res.text();
}

// Helper: render micro templates
function html(strings, ...values){ return String.raw({raw: strings}, ...values); }

// Page initializers
async function initLanding(){
  const ul = document.querySelector('#matchList');
  if (!ul) return;
  try {
    const data = await api('/jobs');
    const items = Array.isArray(data) ? data : (Array.isArray(data?.results) ? data.results : []);
    if (!items.length) throw new Error('empty');
    ul.innerHTML = items.slice(0,5).map(j => html`
      <li class="mb-2">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="fw-semibold">${j.title||j.job_title||'Role'}</div>
            <small class="text-muted">${(j.company||j.company_name||'Company')} • ${(j.location||j.city||'Location')}</small>
          </div>
          <span class="badge bg-light text-dark badge-pill">${(j.match_score? Math.round(j.match_score)+'%':'Match')}</span>
        </div>
      </li>`).join('');
  } catch(e){
    ul.innerHTML = '<li>Data Analyst — Cape Town (92%)</li><li>Operations Lead — Johannesburg (87%)</li><li>Frontend Engineer — Remote (85%)</li>';
  }
  // Revamp modal
  const revampForm = document.getElementById('revampForm');
  if (revampForm){
    revampForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const btn = revampForm.querySelector('button[type="submit"]');
      btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing…';
      try{
        const fd = new FormData(revampForm);
        await api('/revamp', { method:'POST', body: fd, form: true });
        btn.classList.remove('btn-brand'); btn.classList.add('btn-success');
        btn.textContent = 'Done — check your dashboard';
        setTimeout(()=>location.href='/dashboard.html', 900);
      }catch(err){
        alert(err.message||'Revamp failed'); btn.disabled=false; btn.textContent='Revamp';
      }
    });
  }
}

async function initJobs(){
  const getSaved = ()=> JSON.parse(localStorage.getItem('saved_jobs')||'[]');
  const setSaved = (arr)=> localStorage.setItem('saved_jobs', JSON.stringify(arr));

  const list = document.getElementById('jobList');
  const detail = document.getElementById('jobDetail');
  const savedBox = document.getElementById('savedJobs');
  const pager = document.getElementById('pager');
  let jobs = [];
  let currentPage = 1;
  const itemsPerPage = 10;
  if (!list || !detail) return;
  try{
    const data = await api('/jobs');
    jobs = Array.isArray(data) ? data : (Array.isArray(data?.results) ? data.results : []);
    if (!jobs.length) throw new Error('nojobs');
    document.getElementById('count').textContent = jobs.length;
    const renderPage = ()=>{
      const start=(currentPage-1)*itemsPerPage, end=start+itemsPerPage;
      const pageItems = jobs.slice(start,end);
      list.innerHTML = pageItems.map((j,i)=> html`
      <div class="job-item ${i===0?'active':''}" data-index="${start + i}">
        <div class="d-flex justify-content-between">
          <div>
            <div class="fw-semibold">${j.title||j.job_title||'Role'}</div>
            <small class="text-muted">${(j.company||j.company_name||'Company')} • ${(j.location||j.city||'Location')}</small>
          </div>
          <small class="pill">${j.salary_range||j.salary||''}</small>
        </div>
        <small>${(j.skills||[]).slice(0,3).join(', ')||''}</small>
      </div>`).join('');
      if(pager){
        const total = Math.ceil(jobs.length/itemsPerPage)||1;
        pager.querySelector('#pageInfo').textContent = `${currentPage} / ${total}`;
        pager.querySelector('[data-act="prev"]').parentElement.classList.toggle('disabled', currentPage<=1);
        pager.querySelector('[data-act="next"]').parentElement.classList.toggle('disabled', currentPage>=total);
      }
    };
    const show=(idx)=>{
      const j = jobs[idx];
      detail.querySelector('h4').textContent = j.title||j.job_title||'Role';
      detail.querySelector('small.text-muted').textContent = `${(j.company||j.company_name||'Company')} • ${(j.location||j.city||'Location')}`;
      document.getElementById('desc').textContent = j.description||j.summary||'Role description not provided.';
      document.getElementById('reqs').innerHTML = (j.requirements||[]).slice(0,6).map(r=>`<li>${r}</li>`).join('') || '<li>Requirement details shared during interview.</li>';
      const saveBtn = document.querySelector('#saveBtn'); if(saveBtn){ const savedArr = getSaved(); const jid = j.id || j.job_id || j.external_id || String(idx); const isSaved = savedArr.some(x=>String(x.id)===String(jid)); saveBtn.textContent = isSaved ? 'Saved' : 'Save'; saveBtn.onclick = ()=>{ saveToggle(j); saveBtn.textContent = (saveBtn.textContent==='Saved')?'Save':'Saved'; }; }
      document.getElementById('applyBtn').onclick = async ()=>{
        try{
          await api('/apply_job', { method:'POST', body: { job_id: j.id || j.job_id || j.external_id || String(idx) } });
          alert('Application submitted!');
        }catch(e){ alert(e.message||'Apply failed'); }
      };
    };
    show(0);
    list.addEventListener('click', (e)=>{
      const item = e.target.closest('.job-item'); if(!item) return;
      list.querySelectorAll('.job-item').forEach(x=>x.classList.remove('active'));
      item.classList.add('active');
      show(parseInt(item.dataset.index,10));
    });
    if(pager){
      pager.addEventListener('click', (e)=>{
        const a = e.target.closest('[data-act]'); if(!a) return; e.preventDefault();
        const total = Math.ceil(jobs.length/itemsPerPage)||1;
        if(a.dataset.act==='prev' && currentPage>1){ currentPage--; renderPage(); }
        if(a.dataset.act==='next' && currentPage<total){ currentPage++; renderPage(); }
      });
    }
    const renderSaved = ()=>{
      if(!savedBox) return;
      const saved = getSaved();
      savedBox.innerHTML = saved.length ? saved.map(s=>html`<div class="d-flex justify-content-between align-items-center py-1"><small>${s.title} — <span class="text-muted">${s.company||''}</span></small><a class="small" href="#" data-id="${s.id}" data-action="unsave">Remove</a></div>`).join('') : '<small class="text-muted">No saved jobs yet.</small>';
      savedBox.querySelectorAll('[data-action="unsave"]').forEach(a=>a.addEventListener('click',(ev)=>{ev.preventDefault(); const id=a.dataset.id; const arr=getSaved().filter(x=>String(x.id)!==String(id)); setSaved(arr); renderSaved();}));
    };
    const saveToggle = (job)=>{
      const saved = getSaved();
      const idx = saved.findIndex(x=>String(x.id)===String(job.id||job.job_id||job.external_id));
      if(idx>=0){ saved.splice(idx,1); } else { saved.push({ id: job.id||job.job_id||job.external_id||String(Date.now()), title: job.title||job.job_title||'Role', company: job.company||job.company_name||'' }); }
      setSaved(saved);
      renderSaved();
    };
    renderPage();
  }catch(e){
    // leave basic demo items (if present)
  }
}

async function initAuth(){
  const signup = document.getElementById('signupForm');
  if (signup){
    signup.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const fd = new FormData(signup);
      const payload = Object.fromEntries(fd.entries());
      const btn = signup.querySelector('button[type="submit"]'); btn.disabled=true;
      try{
        await api('/signup', { method:'POST', body: payload });
        location.href = '/dashboard.html';
      }catch(err){ alert(err.message||'Sign up failed'); btn.disabled=false; }
    });
  }
  const login = document.getElementById('loginForm');
  if (login){
    login.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const fd = new FormData(login);
      const payload = Object.fromEntries(fd.entries());
      const btn = login.querySelector('button[type="submit"]'); btn.disabled=true;
      try{
        await api('/login', { method:'POST', body: payload });
        location.href = '/dashboard.html';
      }catch(err){ alert(err.message||'Login failed'); btn.disabled=false; }
    });
  }
}

async function initDashboard(){
  const apps = document.getElementById('appsTableBody');
  const sub = document.getElementById('subStatus');
  if (!apps && !sub) return;
  try{
    const data = await api('/applications');
    const rows = (Array.isArray(data)?data:data?.results||[]).slice(0,50).map(a=>html`
      <tr><td>${a.title||a.job_title}</td><td>${a.company||a.company_name||''}</td><td>${a.status||'Pending'}</td><td>${a.updated_at||a.created_at||''}</td></tr>`).join('');
    if (apps) apps.innerHTML = rows || '<tr><td colspan="4" class="text-muted">No applications yet.</td></tr>';
  }catch(e){
    if (apps) apps.innerHTML = '<tr><td colspan="4" class="text-muted">No data right now.</td></tr>';
  }
  try{
    const s = await api('/subscription');
    if (sub) sub.textContent = (s.status||'inactive').toUpperCase();
  }catch(e){ if (sub) sub.textContent = 'INACTIVE'; }
}

async function initRecruiterEmployer(){
  const postForm = document.getElementById('postJobForm');
  if (postForm){
    postForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const payload = Object.fromEntries(new FormData(postForm).entries());
      const btn = postForm.querySelector('button[type="submit"]'); btn.disabled=true;
      try{ await api('/recruiter/jobs', { method:'POST', body: payload }); alert('Job posted'); postForm.reset(); }
      catch(e){ alert(e.message||'Post failed'); }
      finally{ btn.disabled=false; }
    });
  }
  const jobsTable = document.getElementById('recruiterJobs');
  if (jobsTable){
    try{
      const d = await api('/recruiter/jobs');
      const rows = (Array.isArray(d)?d:d?.results||[]).slice(0,100).map(j=>html`
        <tr><td>${j.title}</td><td>${j.location||''}</td><td>${j.status||'Open'}</td><td>${j.applicants_count||0}</td></tr>`).join('');
      jobsTable.innerHTML = rows || '<tr><td colspan="4" class="text-muted">No jobs posted yet.</td></tr>';
    }catch(e){
      jobsTable.innerHTML = '<tr><td colspan="4" class="text-muted">Unable to load jobs.</td></tr>';
    }
  }
}

document.addEventListener('DOMContentLoaded', ()=>{
  initLanding();
  initJobs();
  initAuth();
  initDashboard();
  initRecruiterEmployer();
  const y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
});


async function initStatus(){
  const nav = document.querySelector('nav.nav-wrap');
  if(!nav) return;
  const banner = document.createElement('div');
  banner.id = 'statusBanner';
  banner.className = 'alert alert-secondary mb-0 rounded-0 text-center py-1 small';
  banner.textContent = 'Checking system status…';
  nav.insertAdjacentElement('afterend', banner);
  try{
    const res = await fetch('/api/health', { credentials: 'include' });
    if(!res.ok) throw new Error();
    await res.json().catch(()=>({}));
    banner.className = 'alert alert-success mb-0 rounded-0 text-center py-1 small';
    banner.textContent = 'All systems operational';
    setTimeout(()=>{ banner.remove(); }, 4000);
  }catch(e){
    banner.className = 'alert alert-warning mb-0 rounded-0 text-center py-1 small';
    banner.textContent = 'API is starting up; you can still browse pages.';
  }
}
