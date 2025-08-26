/* Makwande Careers – Page Wiring (Jobs, Dashboards, Recruiter, CV tools, Bursaries, Auth, Subs)
   Assumes you already have the 1-liner:
   window.fetchAPI=(p,o={})=>fetch('/api'+p,{credentials:'include',...o});
*/
(() => {
    // ---------- tiny helpers ----------
    if (!window.fetchAPI) window.fetchAPI=(p,o={})=>fetch('/api'+p,{credentials:'include',...o});
    const $ = (s, r=document) => r.querySelector(s);
    const $$ = (s, r=document) => [...r.querySelectorAll(s)];
    const toJSON = r => r.json().catch(()=> ({}));
    const q = o => new URLSearchParams(o).toString();
    const formDataToObject = f => Object.fromEntries(new FormData(f).entries());
    const toast = (msg, type='success') => {
      const el=document.createElement('div');
      el.className=`toast align-items-center text-bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
      el.innerHTML=`<div class="d-flex"><div class="toast-body">${msg}</div>
        <button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
      document.body.appendChild(el);
      new (window.bootstrap?.Toast ?? class{show(){}})(el, {delay:1800}).show?.();
      el.addEventListener('hidden.bs.toast',()=>el.remove());
    };
    const guard401 = async r => { if (r.status === 401) { location.href = '/login.html'; return null; } return r; };
    const safe = fn => (...a)=>{ try{ return fn(...a);}catch(e){ console.error(e);} };
  
    // ---------- JOBS (jobs.html) ----------
    async function initJobs(){
      const list = $('#jobsList') || $('#jobs');        // container UL/Div
      if (!list) return;
      const search = $('#jobSearch');                   // <input id="jobSearch">
      const locSel = $('#jobLocation');                 // <select id="jobLocation">
      const typeSel = $('#jobType');                    // <select id="jobType">
      const loadMore = $('#jobsMore');                  // <button id="jobsMore">
      let page = 1, size = 20, lastCount = 0, loading = false;
  
      async function fetchJobs(reset=false){
        if (loading) return; loading = true;
        if (reset) { page = 1; list.innerHTML = ''; }
        const params = { page, size };
        if (search?.value) params.search = search.value.trim();
        if (locSel?.value) params.loc = locSel.value;
        if (typeSel?.value) params.type = typeSel.value;
        const r = await fetchAPI('/jobs?'+q(params)); if (!await guard401(r)) return;
        const data = await toJSON(r);
        const jobs = Array.isArray(data?.items) ? data.items : (Array.isArray(data)?data:[]);
        lastCount = jobs.length;
        for (const j of jobs) renderJob(j);
        page++; loading = false;
        if (loadMore) loadMore.classList.toggle('d-none', lastCount < size);
        if (!list.children.length) list.innerHTML = `<div class="text-muted p-3">No jobs found.</div>`;
      }
  
      function renderJob(j){
        const el = document.createElement('div');
        el.className = 'card mb-3';
        el.innerHTML = `
          <div class="card-body d-flex gap-3 flex-wrap align-items-start">
            <div class="flex-grow-1">
              <h6 class="mb-1">${esc(j.title)}</h6>
              <div class="small text-muted">${esc(j.company || '')} · ${esc(j.location || '')}</div>
              <div class="small mt-1">${esc(j.summary || '')}</div>
            </div>
            <div class="d-flex gap-2 ms-auto">
              <a class="btn btn-outline-secondary" href="/jobs.html?id=${encodeURIComponent(j.id||'')}">Details</a>
              <button class="btn btn-primary btn-apply" data-id="${esc(j.id)}">Apply</button>
            </div>
          </div>`;
        list.appendChild(el);
      }
  
      list.addEventListener('click', safe(async e=>{
        const btn = e.target.closest('.btn-apply');
        if (!btn) return;
        const id = btn.dataset.id;
        btn.disabled = true; btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Applying`;
        const r = await fetchAPI('/apply_job',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({job_id:id})});
        if (!await guard401(r)) return;
        toast(r.ok ? 'Application sent' : 'Could not apply', r.ok?'success':'warning');
        btn.disabled = false; btn.textContent = 'Apply';
      }));
  
      search?.addEventListener('input', ()=> fetchJobs(true));
      locSel?.addEventListener('change', ()=> fetchJobs(true));
      typeSel?.addEventListener('change', ()=> fetchJobs(true));
      loadMore?.addEventListener('click', ()=> fetchJobs(false));
  
      // Optional: job details if ?id= present
      const params = new URLSearchParams(location.search);
      const detailId = params.get('id');
      if (detailId && $('#jobDetail')){
        const r = await fetchAPI('/jobs/'+encodeURIComponent(detailId)); if (!await guard401(r)) return;
        const j = await toJSON(r);
        $('#jobDetail').innerHTML = `
          <h4>${esc(j.title||'')}</h4>
          <div class="text-muted mb-2">${esc(j.company||'')} · ${esc(j.location||'')}</div>
          <div class="mb-3">${nl(esc(j.description||''))}</div>
          <button class="btn btn-primary" id="applyDetail" data-id="${esc(j.id)}">Apply</button>`;
        $('#applyDetail')?.addEventListener('click', async ()=>{
          const rr=await fetchAPI('/apply_job',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({job_id:j.id})});
          if (!await guard401(rr)) return;
          toast(rr.ok?'Application sent':'Could not apply', rr.ok?'success':'warning');
        });
      }
  
      fetchJobs(true);
    }
  
    // ---------- CANDIDATE DASHBOARD (dashboard.html) ----------
    async function initCandidateDashboard(){
      const apps = $('#appsList'), saved = $('#savedList');
      if (!apps && !saved) return;
  
      if (apps){
        const r = await fetchAPI('/applications'); if (!await guard401(r)) return;
        const data = await toJSON(r);
        const arr = Array.isArray(data?.items)?data.items:(Array.isArray(data)?data:[]);
        apps.innerHTML = arr.length ? arr.map(a=>`
          <div class="list-group-item">
            <div class="d-flex justify-content-between">
              <div>
                <div class="fw-semibold">${esc(a.title||'')}</div>
                <div class="small text-muted">${esc(a.company||'')} · Applied ${esc(a.applied_at||'')}</div>
              </div>
              <span class="badge text-bg-${badge(a.status)}">${esc(a.status||'pending')}</span>
            </div>
          </div>`).join('') : `<div class="text-muted p-3">No applications yet.</div>`;
      }
  
      if (saved){
        const r = await fetchAPI('/saved_jobs'); if (!await guard401(r)) return;
        const data = await toJSON(r);
        const arr = Array.isArray(data?.items)?data.items:(Array.isArray(data)?data:[]);
        saved.innerHTML = arr.length ? arr.map(j=>`
          <div class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div class="fw-semibold">${esc(j.title||'')}</div>
              <div class="small text-muted">${esc(j.company||'')} · ${esc(j.location||'')}</div>
            </div>
            <button class="btn btn-sm btn-outline-danger unsave" data-id="${esc(j.id)}">Remove</button>
          </div>`).join('') : `<div class="text-muted p-3">No saved jobs.</div>`;
  
        saved.addEventListener('click', safe(async e=>{
          const b = e.target.closest('.unsave'); if (!b) return;
          const r = await fetchAPI('/unsave_job',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({job_id:b.dataset.id})});
          if (!await guard401(r)) return;
          toast('Removed from saved'); b.closest('.list-group-item')?.remove();
        }));
      }
    }
  
    // ---------- RECRUITER (recruiter-dashboard.html, post-job.html) ----------
    async function initRecruiter(){
      const list = $('#recruiterJobs');
      if (list){
        const r = await fetchAPI('/recruiter/jobs'); if (!await guard401(r)) return;
        const data = await toJSON(r);
        const arr = Array.isArray(data?.items)?data.items:(Array.isArray(data)?data:[]);
        list.innerHTML = arr.length ? arr.map(j=>`
          <div class="card mb-2">
            <div class="card-body d-flex justify-content-between flex-wrap gap-2">
              <div>
                <div class="fw-semibold">${esc(j.title||'')}</div>
                <div class="small text-muted">${esc(j.location||'')} · ${esc(j.type||'')}</div>
              </div>
              <div class="d-flex gap-2">
                <a class="btn btn-outline-secondary" href="/jobs.html?id=${encodeURIComponent(j.id||'')}">View</a>
                <button class="btn btn-outline-warning close-job" data-id="${esc(j.id)}">Close</button>
              </div>
            </div>
          </div>`).join('') : `<div class="text-muted p-3">No jobs posted yet.</div>`;
  
        list.addEventListener('click', safe(async e=>{
          const b = e.target.closest('.close-job'); if (!b) return;
          const r = await fetchAPI(`/recruiter/jobs/${encodeURIComponent(b.dataset.id)}`, {method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'closed'})});
          if (!await guard401(r)) return;
          toast(r.ok?'Job closed':'Unable to close', r.ok?'success':'warning');
          if (r.ok) b.closest('.card')?.remove();
        }));
      }
  
      const postForm = $('#postJobForm');
      if (postForm){
        postForm.addEventListener('submit', safe(async e=>{
          e.preventDefault();
          const payload = formDataToObject(postForm);
          const r = await fetchAPI('/recruiter/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
          if (!await guard401(r)) return;
          toast(r.ok?'Job posted':'Failed to post', r.ok?'success':'warning');
          if (r.ok) postForm.reset();
        }));
      }
    }
  
    // ---------- CV Tools (revamp.html, cover_letter.html) ----------
    function initCvTools(){
      const revamp = $('#revampForm'), revOut = $('#revampOut');
      if (revamp){
        revamp.addEventListener('submit', safe(async e=>{
          e.preventDefault();
          const fd = new FormData(revamp);
          const r = await fetchAPI('/revamp', {method:'POST', body: fd});
          if (!await guard401(r)) return;
          const data = await toJSON(r);
          (revOut||revamp).insertAdjacentHTML('afterend', `<div class="alert alert-${r.ok?'success':'warning'} mt-3">${esc(data?.message || 'Done')}</div>`);
        }));
      }
  
      const cov = $('#coverForm'), covOut = $('#coverOut');
      if (cov){
        cov.addEventListener('submit', safe(async e=>{
          e.preventDefault();
          const payload = formDataToObject(cov);
          const r = await fetchAPI('/cover_letter', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
          if (!await guard401(r)) return;
          const data = await toJSON(r);
          (covOut||cov).insertAdjacentHTML('afterend', `<pre class="mt-3 p-3 bg-light rounded border">${esc(data?.content || 'Generated')}</pre>`);
        }));
      }
    }
  
    // ---------- Bursaries ----------
    async function initBursaries(){
      const list = $('#bursaryList');
      if (list){
        const r = await fetchAPI('/bursaries'); if (!await guard401(r)) return;
        const data = await toJSON(r);
        const arr = Array.isArray(data?.items)?data.items:(Array.isArray(data)?data:[]);
        list.innerHTML = arr.length ? arr.map(b=>`
          <div class="card mb-3">
            <div class="card-body d-flex justify-content-between">
              <div>
                <div class="fw-semibold">${esc(b.name||'')}</div>
                <div class="small text-muted">${esc(b.provider||'')}</div>
              </div>
              <a class="btn btn-primary" href="/bursary-apply.html?id=${encodeURIComponent(b.id||'')}">Apply</a>
            </div>
          </div>`).join('') : `<div class="text-muted p-3">No bursaries available.</div>`;
      }
  
      const applyForm = $('#bursaryApplyForm');
      if (applyForm){
        applyForm.addEventListener('submit', safe(async e=>{
          e.preventDefault();
          const fd = new FormData(applyForm);
          const r = await fetchAPI('/bursaries/apply', {method:'POST', body: fd});
          if (!await guard401(r)) return;
          toast(r.ok?'Application submitted':'Could not submit', r.ok?'success':'warning');
          if (r.ok) applyForm.reset();
        }));
      }
    }
  
    // ---------- Auth (login.html, signup.html) ----------
    function initAuth(){
      const login = $('#loginForm');
      login?.addEventListener('submit', safe(async e=>{
        e.preventDefault();
        const payload = formDataToObject(login);
        const r = await fetchAPI('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        if (r.ok) location.href='/dashboard.html'; else toast('Login failed','warning');
      }));
  
      const signup = $('#signupForm');
      signup?.addEventListener('submit', safe(async e=>{
        e.preventDefault();
        const payload = formDataToObject(signup);
        const r = await fetchAPI('/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        if (r.ok) location.href='/dashboard.html'; else toast('Sign up failed','warning');
      }));
    }
  
    // ---------- Subscription (subscription.html) ----------
    async function initSubscription(){
      const statusEl = $('#subStatus'), btnSub = $('#subscribeBtn'), btnCancel = $('#cancelBtn');
      if (!statusEl && !btnSub && !btnCancel) return;
  
      // status
      if (statusEl){
        const r = await fetchAPI('/subscription'); if (!await guard401(r)) return;
        const data = await toJSON(r);
        statusEl.textContent = data?.status || 'inactive';
      }
  
      btnSub?.addEventListener('click', safe(async ()=>{
        const r = await fetchAPI('/subscribe', {method:'POST'});
        if (!await guard401(r)) return;
        toast(r.ok?'Subscribed':'Subscription failed', r.ok?'success':'warning');
        location.reload();
      }));
  
      btnCancel?.addEventListener('click', safe(async ()=>{
        const r = await fetchAPI('/subscription/cancel', {method:'POST'});
        if (!await guard401(r)) return;
        toast(r.ok?'Cancelled':'Cancel failed', r.ok?'success':'warning');
        location.reload();
      }));
    }
  
    // ---------- utils ----------
    const esc = s => (s==null?'':String(s)).replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m]));
    const nl  = s => (s||'').replace(/\n/g,'<br>');
    const badge = s => ({approved:'success', hired:'success', pending:'secondary', rejected:'danger', closed:'dark'}[String(s||'').toLowerCase()] || 'secondary');
  
    // ---------- boot ----------
    document.addEventListener('DOMContentLoaded', () => {
      // Run what’s relevant for the current page:
      initJobs();
      initCandidateDashboard();
      initRecruiter();
      initCvTools();
      initBursaries();
      initAuth();
      initSubscription();
    });
  })();
  