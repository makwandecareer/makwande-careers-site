// auth.js — tiny frontend SDK for AutoApply static pages
// - Handles token storage
// - Retries alternate API routes to avoid 404s
// - Provides login/signup/me/jobs/apply helpers
// - Paints the health badge without "vundefined"

(() => {
  const TOKEN_KEY = "AA_TOKEN";

  // Decide API origin:
  // 1) window.API_ORIGIN (recommended)
  // 2) <meta name="api-origin" content="...">
  // 3) fall back to same origin
  const ORIGIN =
    (typeof window.API_ORIGIN === "string" && window.API_ORIGIN) ||
    (document.querySelector('meta[name="api-origin"]')?.content) ||
    location.origin;

  // Join URL parts, keep "https://" intact
  const join = (...parts) => {
    const s = parts.join("/").replace(/(?<!:)\/{2,}/g, "/");
    return s;
  };

  const API_BASE = join(ORIGIN, "api");

  // --- token helpers ---
  const getToken = () => localStorage.getItem(TOKEN_KEY);
  const saveToken = (t) => localStorage.setItem(TOKEN_KEY, t);
  const clearToken = () => localStorage.removeItem(TOKEN_KEY);
  const requireAuth = () => { if (!getToken()) location.href = "login.html"; };
  const logout = () => { clearToken(); location.href = "login.html"; };

  // --- fetch helpers ---
  const withTimeout = (p, ms = 15000) =>
    Promise.race([p, new Promise((_, r) => setTimeout(() => r(new Error("timeout")), ms))]);

  const doFetch = (url, opts = {}) =>
    withTimeout(fetch(url, opts)).then(async (res) => {
      let data;
      try { data = await res.json(); } catch { data = {}; }
      if (!res.ok) {
        const err = new Error(data.detail || data.message || res.statusText);
        err.status = res.status;
        err.data = data;
        throw err;
      }
      return data;
    });

  const authHeaders = (extra = {}) => {
    const t = getToken();
    return Object.assign({}, extra, t ? { Authorization: `Bearer ${t}` } : {});
  };

  // Try a list of paths until one works; only 404 triggers a retry
  const tryPaths = async (paths, options) => {
    let lastErr;
    for (const p of paths) {
      try { return await doFetch(p, options); }
      catch (e) {
        lastErr = e;
        if (e.status !== 404) throw e;
      }
    }
    throw lastErr || new Error("Not Found");
  };

  // --- API helpers (with alias fallbacks to kill 404s) ---
  async function health() {
    const paths = [ join(ORIGIN, "health"), join(API_BASE, "health") ];
    try {
      const h = await tryPaths(paths, { cache: "no-store" });
      return { ok: !!h.ok, service: h.service, version: h.version };
    } catch {
      return { ok: false };
    }
  }

  async function login(email, password) {
    const body = JSON.stringify({ email, password });
    const options = { method: "POST", headers: { "Content-Type": "application/json" }, body };
    const paths = [ join(API_BASE, "auth/login"), join(API_BASE, "login") ];
    const data = await tryPaths(paths, options);
    if (data.access_token) saveToken(data.access_token);
    return data;
  }

  async function signup(name, email, password) {
    const body = JSON.stringify({ name, email, password });
    const options = { method: "POST", headers: { "Content-Type": "application/json" }, body };
    const paths = [ join(API_BASE, "auth/signup"), join(API_BASE, "signup") ];
    return tryPaths(paths, options);
  }

  const me = () =>
    doFetch(join(API_BASE, "me"), { headers: authHeaders() });

  const listJobs = () =>
    doFetch(join(API_BASE, "jobs"), { headers: authHeaders() });

  const applyJob = (payload) =>
    doFetch(join(API_BASE, "apply_job"), {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload),
    });

  const applications = () =>
    doFetch(join(API_BASE, "applications/protected"), { headers: authHeaders() });

  // --- badge painter (optional) ---
  async function paintBadge() {
    const el = document.getElementById("api-status");
    if (!el) return;
    const h = await health();
    el.textContent = h.ok ? `API connected • v${h.version || "-"}` : "API not reachable";
  }

  // Expose a single global
  window.AutoApply = {
    API_ORIGIN: ORIGIN,
    API_BASE,
    getToken, saveToken, clearToken, requireAuth, logout,
    health, paintBadge,
    login, signup, me, listJobs, applyJob, applications,
    apiFetch: doFetch,
  };

  // Auto-paint the badge if present
  if (document.readyState === "complete" || document.readyState === "interactive") paintBadge();
  else document.addEventListener("DOMContentLoaded", paintBadge);
})();

// auth.js (keep only this file for auth)
const TOKEN_KEY = 'autoapply_token';
const API = (p) => `${(window.API_ORIGIN || '').replace(/\/$/, '')}/api${p}`;

function saveToken(t){ localStorage.setItem(TOKEN_KEY, t); }
function getToken(){ return localStorage.getItem(TOKEN_KEY); }
function logout(){ localStorage.removeItem(TOKEN_KEY); window.location.href = "index.html"; }
function requireAuth(){ if (!getToken()) window.location.href = "index.html"; }

async function apiFetch(path, opts = {}) {
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    (opts.headers || {})
  );
  const t = getToken();
  if (t) headers.Authorization = `Bearer ${t}`;
  const res = await fetch(API(path), { ...opts, headers });
  return res;
}

async function login(email, password) {
  try {
    const res = await apiFetch("/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return { ok:false, message: data.detail || "Invalid credentials" };
    }
    if (!data.access_token) return { ok:false, message:"No token" };
    saveToken(data.access_token);
    return { ok:true };
  } catch {
    return { ok:false, message:"Network error" };
  }
}

async function signup(name, email, password) {
  try {
    const res = await apiFetch("/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) return { ok:false, message: data.detail || "Signup failed" };
    if (!data.access_token) return { ok:false, message:"No token" };
    saveToken(data.access_token);
    return { ok:true };
  } catch { return { ok:false, message:"Network error" }; }
}

async function me() {
  const res = await apiFetch("/me", { method:"GET" });
  return res.ok ? res.json() : null;
}

// expose for pages
window.AutoAuth = { login, signup, logout, getToken, requireAuth, me };
