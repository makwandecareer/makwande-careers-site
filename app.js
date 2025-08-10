import { ENDPOINTS } from "./config.js";

const qs = (sel) => document.querySelector(sel);
const qsa = (sel) => document.querySelectorAll(sel);

const state = {
  page: 1,
  pageSize: 12,
  lastQuery: "",
  lastLocation: "",
};

// --- Auth helpers -----------------------------------------------------------
const getToken = () => localStorage.getItem("aa_token");
const setToken = (t) => localStorage.setItem("aa_token", t);
const clearToken = () => localStorage.removeItem("aa_token");

const authHeaders = () => {
  const t = getToken();
  return t ? { Authorization: Bearer ${t} } : {};
};

// --- UI switches ------------------------------------------------------------
function showAuth() {
  qs("#authView").classList.remove("hidden");
  qs("#jobsView").classList.add("hidden");
  qs("#authedNav").classList.add("hidden");
}

function showJobs() {
  qs("#authView").classList.add("hidden");
  qs("#jobsView").classList.remove("hidden");
  qs("#authedNav").classList.remove("hidden");
}

// --- Tabs (login / signup) --------------------------------------------------
qsa(".tab").forEach((t) =>
  t.addEventListener("click", () => {
    qsa(".tab").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");

    qsa(".panel").forEach((p) => p.classList.remove("active"));
    const name = t.dataset.tab;
    qs(name === "login" ? "#loginForm" : "#signupForm").classList.add("active");
  })
);

// --- Signup -----------------------------------------------------------------
qs("#signupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.currentTarget);
  const payload = {
    full_name: form.get("full_name"),
    email: form.get("email"),
    password: form.get("password"),
  };

  setMsg("#signupMsg", "Creating your account…");
  try {
    const r = await fetch(ENDPOINTS.signup, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data?.detail || "Signup failed");
    setMsg("#signupMsg", "Account created. You can now log in.");
    // switch to login tab
    qs('[data-tab="login"]').click();
  } catch (err) {
    setMsg("#signupMsg", ❌ ${err.message});
  }
});

// --- Login ------------------------------------------------------------------
qs("#loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.currentTarget);
  const payload = {
    email: form.get("email"),
    password: form.get("password"),
  };

  setMsg("#loginMsg", "Logging you in…");
  try {
    const r = await fetch(ENDPOINTS.login, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data?.detail || "Login failed");

    const token = data?.access_token || data?.token || data?.jwt;
    if (!token) throw new Error("API did not return an access token");
    setToken(token);

    await ensureProfile();
    setMsg("#loginMsg", "");
    showJobs();
    await loadJobs();
  } catch (err) {
    setMsg("#loginMsg", ❌ ${err.message});
  }
});

// --- Profile check (optional) -----------------------------------------------
async function ensureProfile() {
  try {
    const r = await fetch(ENDPOINTS.me, { headers: authHeaders() });
    if (!r.ok) throw 0;
    return await r.json();
  } catch {
    // if profile endpoint requires auth and fails, force logout
    // (comment this out if your API doesn't provide /auth/me)
    return null;
  }
}

// --- Jobs search ------------------------------------------------------------
qs("#btnSearch").addEventListener("click", async () => {
  state.page = 1;
  state.lastQuery = qs("#searchInput").value.trim();
  state.lastLocation = qs("#locationSelect").value;
  await loadJobs();
});

qs("#prevPage").addEventListener("click", async () => {
  if (state.page > 1) {
    state.page--;
    await loadJobs();
  }
});

qs("#nextPage").addEventListener("click", async () => {
  state.page++;
  await loadJobs();
});

// --- Logout -----------------------------------------------------------------
qs("#btnLogout").addEventListener("click", () => {
  clearToken();
  showAuth();
});

// --- Utilities --------------------------------------------------------------
function setMsg(sel, text) {
  qs(sel).textContent = text || "";
}

function jobCard(job) {
  const loc = job.location || job.country || "—";
  const company = job.company || job.org || "Company";
  const title = job.title || job.role || "Job";
  const tags = (job.tags || job.skills || []).slice(0, 5);

  const url = job.url || job.apply_url || job.link || "#";
  return `
    <article class="job">
      <h4>${escapeHtml(title)}</h4>
      <div class="company">${escapeHtml(company)} • ${escapeHtml(loc)}</div>
      <div class="tags">
        ${tags.map((t) => <span class="tag">${escapeHtml(t)}</span>).join("")}
      </div>
      <div style="margin-top:10px">
        <a class="btn primary" href="${url}" target="_blank" rel="noopener">View / Apply</a>
      </div>
    </article>
  `;
}

function escapeHtml(s = "") {
  return s.toString().replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[m]));
}

// --- Load jobs from API -----------------------------------------------------
async function loadJobs() {
  const list = qs("#jobsList");
  list.innerHTML = "<div class='card'>Loading jobs…</div>";

  // Build query params according to your backend shape.
  // Common patterns: q, page, limit / page_size, location
  const params = new URLSearchParams();
  if (state.lastQuery) params.set("q", state.lastQuery);
  if (state.lastLocation) params.set("location", state.lastLocation);
  params.set("page", String(state.page));
  params.set("page_size", String(state.pageSize));

  try {
    const r = await fetch(${ENDPOINTS.jobs}?${params.toString()}, {
      headers: { "Content-Type": "application/json", ...authHeaders() },
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data?.detail || "Failed to load jobs");

    // Accept a few common API shapes:
    const jobs = data.items || data.results || data.data || data.jobs || [];
    const total = data.total || data.count || jobs.length;
    const hasNext = total > state.page * state.pageSize || data.next || data.has_next;

    list.innerHTML = jobs.length
      ? jobs.map(jobCard).join("")
      : "<div class='card'>No jobs found.</div>";

    updatePager(hasNext);
  } catch (err) {
    list.innerHTML = <div class='card'>❌ ${escapeHtml(err.message)}</div>;
    updatePager(false);
  }
}

function updatePager(hasNext) {
  qs("#pageInfo").textContent = Page ${state.page};
  qs("#prevPage").disabled = state.page <= 1;
  qs("#nextPage").disabled = !hasNext;
}

// --- Init -------------------------------------------------------------------
(function init() {
  qs("#year").textContent = new Date().getFullYear();
  if (getToken()) {
    showJobs();
    loadJobs();
  } else {
    showAuth();
  }
})();