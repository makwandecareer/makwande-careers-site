// scripts/login.js
// Full login handler for AutoApplyApp

(function () {
    "use strict";
  
    // --- Resolve API base URL from whatever config style you used ---
    const API_BASE =
      (window.CONFIG && window.CONFIG.API_BASE_URL) ||
      (window._CONFIG_ && window._CONFIG_.API_BASE_URL) ||
      (typeof API_BASE_URL !== "undefined" ? API_BASE_URL : "");
  
    if (!API_BASE) {
      console.error("API base URL is missing. Make sure scripts/config.js runs first.");
    }
  
    // Elements
    const form = document.querySelector("#loginForm");
    const emailInput = document.querySelector("#email");
    const passwordInput = document.querySelector("#password");
    const statusEl = document.querySelector("#loginStatus");
  
    function setStatus(msg, ok = false) {
      if (!statusEl) return;
      statusEl.textContent = msg || "";
      statusEl.style.color = ok ? "green" : "crimson";
    }
  
    async function login(evt) {
      evt.preventDefault();
      setStatus("");
  
      const email = (emailInput?.value || "").trim();
      const password = passwordInput?.value || "";
  
      if (!email || !password) {
        setStatus("Please enter email and password.");
        return;
      }
  
      try {
        const res = await fetch(${API_BASE}/login, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          // If your backend expects form data instead, swap body for URLSearchParams
          body: JSON.stringify({ email, password }),
        });
  
        // Try to parse JSON (even on non-2xx to read message)
        let data = null;
        try { data = await res.json(); } catch (_) {}
  
        if (!res.ok) {
          const msg =
            (data && (data.detail || data.message)) ||
            Login failed (HTTP ${res.status}).;
          setStatus(msg);
          return;
        }
  
        // Expecting: { token: "..." }  (change if your backend returns a different key)
        const token = (data && (data.token || data.access_token)) || "";
        if (!token) {
          setStatus("Login failed: no token returned.");
          return;
        }
  
        // Save and go to Jobs
        localStorage.setItem("authToken", token);
        localStorage.setItem("authEmail", email);
        setStatus("Login successful. Redirecting…", true);
  
        // Change the next line if your page name/path differs
        window.location.href = "/jobs.html";
      } catch (err) {
        console.error(err);
        setStatus("Network error contacting server.");
      }
    }
  
    // Attach handler
    if (form) form.addEventListener("submit", login);
  })();
  
  Expected HTML (example):
  
  <!-- login.html -->
  <form id="loginForm">
    <input id="email" type="email" placeholder="Email" />
    <input id="password" type="password" placeholder="Password" />
    <button type="submit">Log In</button>
  </form>
  <p id="loginStatus"></p>
  
  <!-- Load config first, then login.js -->
  <script src="/scripts/config.js"></script>
  <script src="/scripts/login.js"></script>
  