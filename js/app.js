// Base URL (user can override via localStorage)
window.API_BASE = localStorage.getItem('apiBase') || 'http://127.0.0.1:8000';

// Helpers
async function fetchJson(path, options = {}) {
  const res = await fetch(`${window.API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.json();
}
function setApiBase(url) {
  if (!url) return;
  localStorage.setItem('apiBase', url);
  window.API_BASE = url;
}
function getQueryParam(key) {
  const url = new URL(location.href);
  return url.searchParams.get(key);
}
window.app = { fetchJson, setApiBase, API_BASE: () => window.API_BASE, getQueryParam };

// Common DOM ready
window.addEventListener('DOMContentLoaded', () => {
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  document.body.addEventListener('click', (e) => {
    const el = e.target.closest('[data-api-base]');
    if (el) {
      const next = prompt('Set API base URL', window.API_BASE);
      - alert('API base saved. Reloading…'); location.reload();
+ alert('API base saved. Reloading...'); location.reload();

      if (next) { setApiBase(next); alert('API base saved. Reloading…'); location.reload(); }
    }
  });
});

// ---- Existing page bootstraps (stories/metrics/partners/etc.) ----
(async function hydrate() {
  try {
    // Candidates stories
    const tWrap = document.getElementById('testimonials');
    if (tWrap) {
      const rows = await fetchJson('/api/public/candidate-stories');
      tWrap.innerHTML = rows.map(r => `
        <div class="card">
          <div class="row"><span class="badge success">Hired</span><span class="badge">${r.country}</span></div>
          <h3>${r.name} — ${r.role}</h3>
          <p>${r.story}</p>
        </div>`).join('');
    }

    // Investors metrics
    const mWrap = document.getElementById('metrics');
    if (mWrap) {
      const m = await fetchJson('/api/public/metrics');
      mWrap.innerHTML = `
        <div class="grid grid-3">
          <div class="card stat"><span class="stat-label">Monthly Active</span><span class="stat-value">${m.monthly_active_users?.toLocaleString?.() ?? m.monthly_active_users}</span></div>
          <div class="card stat"><span class="stat-label">Paid Subscribers</span><span class="stat-value">${m.paid_subscribers}</span></div>
          <div class="card stat"><span class="stat-label">Jobs Indexed</span><span class="stat-value">${m.jobs_indexed}</span></div>
        </div>`;
      const cap = document.getElementById('cap-table-body');
      if (cap && m.cap_table) {
        cap.innerHTML = m.cap_table.map(r => `<tr><td>${r.holder}</td><td>${r.shares}</td><td>${r.ownership}%</td></tr>`).join('');
      }
    }

    // Partnerships list
    const pList = document.getElementById('partners-list');
    if (pList) {
      const partners = await fetchJson('/api/partners');
      pList.innerHTML = partners.map(p => `<tr><td>${p.name}</td><td>${p.type}</td><td>${p.country}</td><td>${p.status}</td></tr>`).join('');
    }
    const pForm = document.getElementById('partner-form');
    if (pForm) {
      pForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(pForm).entries());
        await fetchJson('/api/partners/propose', { method: 'POST', body: JSON.stringify(data) });
        alert('Proposal sent. We’ll be in touch.');
        pForm.reset();
      });
    }

    // Marketing campaigns
    const cBody = document.getElementById('campaigns-body');
    if (cBody) {
      const campaigns = await fetchJson('/api/public/campaigns');
      cBody.innerHTML = campaigns.map(c => `<tr>
        <td>${c.name}</td><td>${c.channel}</td><td>${c.status}</td><td>${c.ctr}%</td><td>R${c.spend}</td></tr>`).join('');
    }

    // Brand collaborations
    const bcBody = document.getElementById('collabs-body');
    if (bcBody) {
      const collabs = await fetchJson('/api/public/collaborations');
      bcBody.innerHTML = collabs.map(x => `<tr><td>${x.brand}</td><td>${x.campaign}</td><td>${x.region}</td><td>${x.result}</td></tr>`).join('');
    }
    const bcForm = document.getElementById('collab-form');
    if (bcForm) {
      bcForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(bcForm).entries());
        await fetchJson('/api/brands/collaborate', { method:'POST', body: JSON.stringify(data) });
        alert('Thanks! We’ll review your collaboration request.');
        bcForm.reset();
      });
    }

    // ---- Bursaries board ----
    const bBody = document.getElementById('bursaries-body');
    if (bBody) await window.app.loadBursaries?.();
  } catch (err) {
    console.error(err);
  }
})();

// Public function to load bursaries (used by bursaries.html)
window.app.loadBursaries = async function() {
  const bBody = document.getElementById('bursaries-body');
  if (!bBody) return;
  const q = document.getElementById('q')?.value?.trim() || '';
  const country = document.getElementById('country')?.value || '';
  const field = document.getElementById('field')?.value?.trim() || '';
  const minAmount = document.getElementById('minAmount')?.value || '';
  const params = new URLSearchParams({ q, country, field, min_amount: minAmount }).toString();
  const rows = await fetchJson(`/api/public/bursaries?${params}`);
  bBody.innerHTML = rows.map(b => `
    <tr>
      <td>${b.title}</td>
      <td>${b.provider}</td>
      <td>${b.country}</td>
      <td>${b.field_of_study}</td>
      <td>R${b.amount}</td>
      <td>${b.deadline}</td>
      <td><a class="btn btn-ghost" href="/bursary-apply.html?id=${b.id}">Apply</a></td>
    </tr>
  `).join('') || `<tr><td colspan="7">No bursaries found.</td></tr>`;
};

// Hydrate bursary-apply page
window.app.hydrateBursaryApply = async function() {
  const id = getQueryParam('id');
  if (!id) return;
  const bursary = await fetchJson(`/api/public/bursaries/${id}`);
  document.getElementById('bursary_id').value = bursary.id;
  document.getElementById('bursary-title').textContent = bursary.title;
  document.getElementById('bursary-sub').textContent = `${bursary.provider} • ${bursary.country}`;
  document.getElementById('bursary-about').textContent = bursary.description;
  document.getElementById('bursary-country').textContent = bursary.country;
  document.getElementById('bursary-field').textContent = bursary.field_of_study;
  document.getElementById('bursary-amount').textContent = `R${bursary.amount}`;
  document.getElementById('bursary-deadline').textContent = `Deadline: ${bursary.deadline}`;

  const form = document.getElementById('apply-form');
  const msg = document.getElementById('apply-msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = 'Submitting…';
    const data = Object.fromEntries(new FormData(form).entries());
    try {
      await fetchJson('/api/bursaries/apply', { method: 'POST', body: JSON.stringify(data) });
      msg.textContent = 'Application submitted! We emailed you a confirmation.';
      form.reset();
    } catch (err) {
      msg.textContent = `Error: ${err.message}`;
    }
  });
};


