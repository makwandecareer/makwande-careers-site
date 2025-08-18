/* auth.js — final, single source of truth
   - Calls ONLY the new routes: /api/login, /api/signup, /api/me, /api/jobs, /api/apply_job, /api/applications/protected, /api/health
   - Single token key
   - Health badge painter (no "vundefined")
   - Exposes one API: window.AutoAuth (and aliases window.AutoApply = AutoAuth)
*/
(() => {
  'use strict';

  // ---- Config --------------------------------------------------------------
  const TOKEN_KEY = 'autoapply_token';
  const DEFAULT_API_ORIGIN = 'https://autoapply-api.onrender.com';

  // Resolve API origin (window var -> <meta> -> default)
  const API_ORIGIN =
    (typeof window.API_ORIGIN === 'string' && window.API_ORIGIN.trim()) ||
    (document.querySelector('meta[name="api-origin"]')?.content) ||
    DEFAULT_API_ORIGIN;

  // Build full URL safely
  const API = (path) =>
    `${API_ORIGIN.replace(/\/+$/,'')}/api${path.startsWith('/') ? path : '/'+path}`;

  // ---- Token helpers -------------------------------------------------------
  const saveToken   = (t) => localStorage.setItem(TOKEN_KEY, t);
  const getToken    = ()   => localStorage.getItem(TOKEN_KEY);
  const clearToken  = ()   => localStorage.removeItem(TOKEN_KEY);
  const logout      = ()   => { clearToken(); location.href = 'login.html'; };
  const requireAuth = ()   => { if (!getToken()) location.href = 'login.html'; };

  // ---- Fetch helpers -------------------------------------------------------
  const withTimeout = (p, ms=15000) =>
    Promise.race([ p, new Promise((_,r)=>setTimeout(()=>r(new Error('timeout')), ms)) ]);

  async function doFetch(url, opts={}) {
    const headers = Object.assign(
      { 'Content-Type': 'application/json' },
      opts.headers || {}
    );
    const t = getToken();
    if (t) headers.Authorization = `Bearer ${t}`;

    const res = await withTimeout(fetch(url, { ...opts, headers }));
    let data = null;
    try { data = await res.json(); } catch { /* no body */ }

    if (!res.ok) {
      const msg = (data && (data.detail || data.message)) || res.statusText || 'Request failed';
      const err = new Error(msg);
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  // ---- API calls (new, stable paths) --------------------------------------
  async function login(email, password) {
    const data = await doFetch(API('/login'), {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (!data || !data.access_token) throw new Error('No token in response');
    saveToken(data.access_token);
    return data;
  }

  async function signup(name, email, password) {
    const data = await doFetch(API('/signup'), {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
    if (data && data.access_token) saveToken(data.access_token);
    return data;
  }

  const me            = () => doFetch(API('/me'), { method: 'GET' });
  const listJobs      = () => doFetch(API('/jobs'), { method: 'GET' });
  const applications  = () => doFetch(API('/applications/protected'), { method: 'GET' });
  const applyJob      = (payload) =>
    doFetch(API('/apply_job'), { method: 'POST', body: JSON.stringify(payload) });

  // Health (try /api/health first; fall back to /health if present)
  async function health() {
    try {
      return await doFetch(API('/health'), { method: 'GET', cache: 'no-store' });
    } catch (e) {
      try {
        const url = `${API_ORIGIN.replace(/\/+$/,'')}/health`;
        return await doFetch(url, { method: 'GET', cache: 'no-store' });
      } catch {
        return { ok:false };
      }
    }
  }

  // ---- Badge painter -------------------------------------------------------
  async function paintBadge() {
    const el = document.getElementById('api-status');
    if (!el) return;
    try {
      const h = await health();
      el.textContent = h && h.ok
        ? `API connected • v${h.version || '-'}`
        : 'API not reachable';
    } catch {
      el.textContent = 'API not reachable';
    }
  }

  // ---- Public API ----------------------------------------------------------
  const AutoAuth = {
    // config
    API_ORIGIN,
    API,

    // token & nav
    saveToken, getToken, clearToken, requireAuth, logout,

    // calls
    login, signup, me, listJobs, applications, applyJob, health, paintBadge,
  };

  // Expose
  window.AutoAuth = AutoAuth;
  // Backwards-friendly alias if some pages still reference AutoApply.*
  window.AutoApply = AutoAuth;

  // Auto paint the badge if present
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', paintBadge);
  } else {
    paintBadge();
  }
})();
