/* static/js/main.js
   Global helpers used across pages. Defines: apiFetch, apiJSON, setSignedInUI, requireAuth, showStatusBanner.
   Make sure this file is loaded BEFORE any page-specific scripts. */

   (function () {
    const $ = (s) => document.querySelector(s);
  
    // Always route requests through the static-site proxy (/api/*)
    function apiPath(path) {
      if (!path) return "/api";
      return "/api" + (path.startsWith("/") ? path : "/" + path);
    }
  
    // Fetch with Authorization header when a token exists
    window.apiFetch = function (path, opts = {}) {
      const token = localStorage.getItem("AA_TOKEN");
      const headers = Object.assign(
        {},
        opts.headers || {},
        token ? { Authorization: `Bearer ${token}` } : {}
      );
  
      return fetch(apiPath(path), Object.assign({}, opts, { headers }));
    };
  
    // Robust JSON fetch: parses JSON when available, falls back to text, throws on !ok
    window.apiJSON = async function (path, opts = {}) {
      const res = await window.apiFetch(path, opts);
      const ct = (res.headers.get("content-type") || "").toLowerCase();
      const body = ct.includes("application/json") ? await res.json() : { detail: await res.text() };
      if (!res.ok) throw new Error(body?.detail || `HTTP ${res.status}`);
      return body;
    };
  
    // Toggle navbar buttons based on auth state
    window.setSignedInUI = function () {
      const signedIn = !!localStorage.getItem("AA_TOKEN");
      const btnLogin  = $("#btnLogin");
      const btnSignup = $("#btnSignup");
      const btnLogout = $("#btnLogout");
      if (!btnLogin || !btnSignup || !btnLogout) return;
  
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
    };
  
    // Redirect to login if there is no token
    window.requireAuth = function () {
      const token = localStorage.getItem("AA_TOKEN");
      if (!token) { location.href = "/login.html"; return false; }
      return true;
    };
  
    // Optional status banner: shows API connectivity if elements exist
    window.showStatusBanner = async function () {
      const banner = $("#statusBanner");
      const text   = $("#statusText");
      if (!banner || !text) return;
  
      try {
        const j = await window.apiJSON("/health");
        text.textContent = `API connected • v${j.version}`;
      } catch (_) {
        text.textContent = "API not reachable";
      }
      banner.classList.remove("d-none");
    };
  
    // Common on-load hooks (safe on any page)
    document.addEventListener("DOMContentLoaded", () => {
      const y = $("#year");
      if (y) y.textContent = new Date().getFullYear();
  
      window.setSignedInUI();
      window.showStatusBanner();
    });
  })();
  



