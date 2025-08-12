/* Shared helpers to keep every page consistent and CORS-free via /api proxy */
(function () {
  const $ = (s) => document.querySelector(s);

  // Always talk to /api/*
  const apiPath = (path) => "/api" + (path.startsWith("/") ? path : "/" + path);

  // Fetch that auto-attaches Bearer token when present
  window.apiFetch = async function (path, opts = {}) {
    const token = localStorage.getItem("AA_TOKEN");
    const headers = Object.assign(
      {},
      opts.headers || {},
      token ? { Authorization: `Bearer ${token}` } : {}
    );
    return fetch(apiPath(path), Object.assign({}, opts, { headers }));
  };

  // JSON fetch with robust parsing + error surfacing
  window.apiJSON = async function (path, opts = {}) {
    const res = await window.apiFetch(path, opts);
    const ct = res.headers.get("content-type") || "";
    const body = ct.includes("application/json")
      ? await res.json()
      : { detail: await res.text() };
    if (!res.ok) throw new Error(body?.detail || `HTTP ${res.status}`);
    return body;
  };

  // Navbar auth state
  window.setSignedInUI = function () {
    const signedIn = !!localStorage.getItem("AA_TOKEN");
    const btnLogin = $("#btnLogin");
    const btnSignup = $("#btnSignup");
    const btnLogout = $("#btnLogout");
    if (btnLogin && btnSignup && btnLogout) {
      if (signedIn) {
        btnLogin.classList.add("d-none");
        btnSignup.classList.add("d-none");
        btnLogout.classList.remove("d-none");
      } else {
        btnLogin.classList.remove("d-none");
        btnSignup.classList.remove("d-none");
        btnLogout.classList.add("d-none");
      }
      btnLogout.onclick = () => {
        localStorage.clear();
        location.href = "/login.html";
      };
    }
  };

  // Require auth for protected pages
  window.requireAuth = function () {
    const token = localStorage.getItem("AA_TOKEN");
    if (!token) { location.href = "/login.html"; return false; }
    return true;
  };

  // Status banner (needs /api/health on backend)
  window.showStatusBanner = async function () {
    const banner = $("#statusBanner");
    const text = $("#statusText");
    if (!banner || !text) return;
    try {
      const j = await apiJSON("/health");
      text.textContent = `API connected • v${j.version}`;
    } catch (_) {
      text.textContent = "API not reachable";
    }
    banner.classList.remove("d-none");
  };

  // Common init on every page
  document.addEventListener("DOMContentLoaded", () => {
    const y = $("#year");
    if (y) y.textContent = new Date().getFullYear();
    window.setSignedInUI();
    window.showStatusBanner();
  });
})();




