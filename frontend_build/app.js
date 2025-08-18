// ====== Config ======
const API_BASE = "https://autoapply-api.onrender.com"; // set to "" to disable API
const CSV_URL  = "jobs.csv";                             // local fallback

// ====== Helpers ======
const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function sanitize(s) {
  return String(s ?? "").replace(/[<>]/g, c => ({'<':'&lt;','>':'&gt;'}[c]));
}
function uniqueSorted(arr) {
  return [...new Set(arr.filter(Boolean))].sort((a,b)=>a.localeCompare(b));
}

// ====== Data loading ======
async function fetchFromApi() {
  if (!API_BASE) throw new Error("API disabled");
  const res = await fetch(${API_BASE.replace(/\/$/,'')}/api/jobs?limit=1000&ts=${Date.now()}, {cache:'no-store'});
  if (!res.ok) throw new Error(API ${res.status});
  return res.json();
}
function fetchFromCsv() {
  return new Promise((resolve, reject) => {
    if (typeof Papa === "undefined") return reject(new Error("PapaParse missing"));
    Papa.parse(CSV_URL, {
      header: true,
      download: true,
      dynamicTyping: false,
      complete: (r) => resolve(r.data.filter(row => Object.keys(row).length > 1)),
      error: reject
    });
  });
}

async function loadJobs() {
  try {
    const jobs = await fetchFromApi();
    setLastUpdated("API");
    return normalize(jobs);
  } catch (e) {
    console.warn("API failed, trying CSV…", e);
    const jobs = await fetchFromCsv();
    setLastUpdated("CSV");
    return normalize(jobs);
  }
}

function normalize(rows) {
  return rows.map(r => ({
    id:        r.id || r.ID || cryptoRandom(),
    title:     r.title || r.TITLE || "",
    company:   r.company || r.COMPANY || "",
    location:  r.location || r.LOCATION || "",
    url:       r.url || r.URL || "#",
    description: r.description || r.DESCRIPTION || "",
    source:    r.source || r.SOURCE || "",
    posted_at: r.posted_at || r.POSTED_AT || ""
  }));
}
function cryptoRandom() {
  try { return crypto.randomUUID(); }
  catch { return String(Math.random()).slice(2); }
}

function setLastUpdated(source) {
  const el = $("#lastUpdated");
  if (!el) return;
  el.textContent = Last updated via ${source} — ${new Date().toLocaleString()};
}

// ====== Rendering ======
function renderFilters(jobs) {
  const locSel = $("#locFilter");
  const srcSel = $("#sourceFilter");
  if (!locSel || !srcSel) return;

  const locs = uniqueSorted(jobs.map(j => j.location));
  const srcs = uniqueSorted(jobs.map(j => j.source));

  locSel.innerHTML = <option value="">All</option> + locs.map(l=><option>${sanitize(l)}</option>).join("");
  srcSel.innerHTML = <option value="">All</option> + srcs.map(s=><option>${sanitize(s)}</option>).join("");
}

function renderJobs(jobs, q = "", loc = "", src = "") {
  const list = $("#jobsList");
  const empty = $("#emptyState");
  if (!list || !empty) return;

  const term = q.trim().toLowerCase();
  const filtered = jobs.filter(j => {
    const matchQ = !term || [j.title,j.company,j.location,j.description].join(" ").toLowerCase().includes(term);
    const matchL = !loc || j.location === loc;
    const matchS = !src || j.source === src;
    return matchQ && matchL && matchS;
  });

  if (filtered.length === 0) {
    list.innerHTML = "";
    empty.classList.remove("hidden");
    return;
  }

  empty.classList.add("hidden");
  list.innerHTML = filtered.map(j => `
    <article class="job">
      <h3>${sanitize(j.title)} <span class="badge">${sanitize(j.company)}</span></h3>
      <div class="meta">${sanitize(j.location || "Remote")} • ${sanitize(j.source || "Source")}</div>
      <p class="muted">${sanitize(j.description).slice(0, 220)}${j.description.length>220?'…':''}</p>
      <div class="actions">
        <a class="btn btn-primary" href="${sanitize(j.url)}" target="_blank" rel="noopener">View & Apply</a>
      </div>
    </article>
  `).join("");
}

// ====== Page bootstrap ======
document.addEventListener("DOMContentLoaded", async () => {
  // Year in footer
  const y = $("#year"); if (y) y.textContent = new Date().getFullYear();

  // Only run on jobs.html
  if (!$("#jobsList")) return;

  let JOBS = [];
  try {
    JOBS = await loadJobs();
    renderFilters(JOBS);
    renderJobs(JOBS);
  } catch (e) {
    console.error("Failed to load jobs:", e);
    const empty = $("#emptyState");
    if (empty) {
      empty.classList.remove("hidden");
      empty.querySelector("p").textContent = "We couldn’t load jobs right now. Please try again later.";
    }
  }

  // Wire filters safely
  const q = $("#q"), loc = $("#locFilter"), src = $("#sourceFilter");
  const rerender = () => renderJobs(JOBS, q?.value || "", loc?.value || "", src?.value || "");

  q && q.addEventListener("input", rerender);
  loc && loc.addEventListener("change", rerender);
  src && src.addEventListener("change", rerender);
});
