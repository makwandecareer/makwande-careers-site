// Read API base URL
const API = (window.CONFIG && window.CONFIG.API_BASE_URL)
  ? window.CONFIG.API_BASE_URL.replace(/\/+$/, '')
  : 'https://autoapplyapp-api.onrender.com';

// Token from login
const token = localStorage.getItem('token') || '';

// Elements
const elUser     = document.getElementById('currentUser');
const elLogout   = document.getElementById('logoutBtn');
const elJobsList = document.getElementById('jobsList');
const elJobsStat = document.getElementById('jobsStatus');
const elJobsDot  = document.getElementById('jobsDot');
const elApiStat  = document.getElementById('apiStatus');
const elApiDot   = document.getElementById('apiDot');

function authHeaders() {
  const h = { 'Content-Type': 'application/json' };
  if (token) h['Authorization'] = 'Bearer ' + token;
  return h;
}

function setDot(el, ok) {
  el.classList.remove('ok', 'err');
  el.classList.add(ok ? 'ok' : 'err');
}

async function checkApi() {
  try {
    const r = await fetch(API + '/health', { headers: authHeaders() });
    const ok = r.ok;
    setDot(elApiDot, ok);
    elApiStat.textContent = ok ? 'API online' : `API error (${r.status})`;
  } catch (e) {
    setDot(elApiDot, false);
    elApiStat.textContent = 'API unreachable';
  }
}

async function loadMe() {
  if (!token) {
    elUser.textContent = 'Not signed in';
    return;
  }
  try {
    const r = await fetch(API + '/auth/me', { headers: authHeaders() });
    if (r.ok) {
      const me = await r.json();
      elUser.textContent = me.name ? `${me.name} • ${me.email || ''}`.trim() : (me.email || 'Signed in');
    } else {
      elUser.textContent = 'Auth expired — log in again';
    }
  } catch {
    elUser.textContent = 'Unable to fetch user';
  }
}

function jobCard(job) {
  const title    = job.title || job.position || 'Untitled';
  const company  = job.company || job.org || 'Unknown company';
  const location = job.location || job.city || '—';
  const link     = job.url || job.link || '#';

  const div = document.createElement('div');
  div.className = 'job';

  const t = document.createElement('div');
  t.className = 'title';
  t.textContent = title;

  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.innerHTML = `
    <span>${company}</span>
    <span>•</span>
    <span>${location}</span>
    ${link && link !== '#' ? `<span>•</span><a href="${link}" target="_blank" rel="noopener">View</a>` : ''}
  `;

  const row = document.createElement('div');
  row.className = 'row';
  const btn = document.createElement('button');
  btn.className = 'btn accent';
  btn.textContent = 'Apply';
  btn.onclick = async () => {
    btn.disabled = true;
    btn.textContent = 'Applying…';
    try {
      const res = await fetch(API + '/jobs/apply', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ jobId: job.id || job._id || job.url || '' })
      });
      btn.textContent = res.ok ? 'Applied ✓' : 'Failed';
    } catch {
      btn.textContent = 'Error';
    }
  };

  row.appendChild(btn);
  div.appendChild(t);
  div.appendChild(meta);
  div.appendChild(row);
  return div;
}

async function loadJobs() {
  elJobsList.innerHTML = '';
  setDot(elJobsDot, true);
  try {
    const r = await fetch(API + '/jobs', { headers: authHeaders() });
    if (!r.ok) {
      setDot(elJobsDot, false);
      elJobsStat.querySelector('span:last-child').textContent = `Failed (${r.status})`;
      elJobsList.innerHTML = `<div class="empty">Couldn’t load jobs.</div>`;
      return;
    }
    const data = await r.json();
    const jobs = Array.isArray(data) ? data : (data.jobs || []);
    elJobsStat.querySelector('span:last-child').textContent = `Loaded ${jobs.length} job${jobs.length === 1 ? '' : 's'}`;
    if (jobs.length === 0) {
      elJobsList.innerHTML = `<div class="empty">No jobs yet.</div>`;
      return;
    }
    jobs.slice(0, 20).forEach(j => elJobsList.appendChild(jobCard(j)));
  } catch (e) {
    setDot(elJobsDot, false);
    elJobsStat.querySelector('span:last-child').textContent = 'Network error';
    elJobsList.innerHTML = `<div class="empty">Network error.</div>`;
  }
}

elLogout.addEventListener('click', async () => {
  try {
    await fetch(API + '/auth/logout', { method: 'POST', headers: authHeaders() });
  } catch {}
  localStorage.removeItem('token');
  location.href = '/login.html';
});

// Init
checkApi();
loadMe();
loadJobs();

