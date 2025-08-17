<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Makwande Careers — Jobs</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background:#f8f9fa; }
    .job-card { transition: box-shadow .2s ease; }
    .job-card:hover { box-shadow: 0 10px 24px rgba(0,0,0,.08); }
  </style>
</head>
<body>
<nav class="navbar navbar-expand-lg bg-white border-bottom">
  <div class="container">
    <a class="navbar-brand fw-bold" href="index.html">Makwande Careers</a>
    <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav"><span class="navbar-toggler-icon"></span></button>
    <div class="collapse navbar-collapse" id="nav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="jobs.html">Jobs</a></li>
        <li class="nav-item"><a class="nav-link" href="revamp.html">CV Revamp</a></li>
        <li class="nav-item"><a class="nav-link" href="dashboard.html">Dashboard</a></li>
        <li class="nav-item"><a class="btn btn-primary ms-lg-3" href="login.html">Login</a></li>
      </ul>
    </div>
  </div>
</nav>

<section class="py-4">
  <div class="container">

    <!-- Controls -->
    <div class="card border-0 shadow-sm mb-3">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-12 col-md-4">
            <label class="form-label">Search</label>
            <input id="searchInput" class="form-control" placeholder="Title, company, keyword...">
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label">Location</label>
            <select id="locationFilter" class="form-select"><option value="">All</option></select>
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label">Company</label>
            <select id="companyFilter" class="form-select"><option value="">All</option></select>
          </div>
          <div class="col-6 col-md-2">
            <label class="form-label d-block">Remote</label>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" id="remoteOnly">
              <label class="form-check-label" for="remoteOnly">Remote only</label>
            </div>
          </div>
          <div class="col-12 col-md-12 text-end">
            <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addJobModal">
              + Add Job
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Jobs list -->
    <div id="jobsList" class="row g-3"></div>

    <!-- Empty state -->
    <div id="emptyState" class="text-center text-muted py-5 d-none">
      <p class="mb-2">No jobs found.</p>
      <p class="small">Try clearing filters or add a job.</p>
    </div>
  </div>
</section>

<!-- Add Job Modal -->
<div class="modal fade" id="addJobModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <form id="addJobForm">
        <div class="modal-header">
          <h5 class="modal-title">Add a Job</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Job Title *</label>
              <input required name="title" class="form-control" placeholder="e.g. Data Analyst">
            </div>
            <div class="col-md-6">
              <label class="form-label">Company *</label>
              <input required name="company" class="form-control" placeholder="e.g. Acme Ltd">
            </div>
            <div class="col-md-6">
              <label class="form-label">Location *</label>
              <input required name="location" class="form-control" placeholder="e.g. Johannesburg">
            </div>
            <div class="col-md-6">
              <label class="form-label">Country</label>
              <input name="country" class="form-control" placeholder="e.g. South Africa">
            </div>
            <div class="col-md-6">
              <label class="form-label">Closing Date</label>
              <input type="date" name="closing_date" class="form-control">
            </div>
            <div class="col-md-6">
              <label class="form-label">Apply URL *</label>
              <input required type="url" name="apply_url" class="form-control" placeholder="https://...">
            </div>
            <div class="col-12">
              <label class="form-label">Description *</label>
              <textarea required name="description" rows="5" class="form-control" placeholder="Key responsibilities, requirements..."></textarea>
            </div>
            <div class="col-12">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" name="remote">
                <label class="form-check-label">Remote role</label>
              </div>
            </div>

            <!-- Optional: backend POST -->
            <div class="col-12">
              <details class="mt-2">
                <summary class="small text-muted">Optional: Send to backend (if enabled)</summary>
                <div class="row g-2 mt-1">
                  <div class="col-md-8">
                    <input id="apiBase" class="form-control" placeholder="API base (e.g. https://api.autoapply-...co.za)">
                  </div>
                  <div class="col-md-4">
                    <input id="apiKey" class="form-control" placeholder="X-API-Key (optional)">
                  </div>
                </div>
              </details>
            </div>

          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Job</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // ===== Minimal config =====
  // If you later have a backend, put it here or in the modal field.
  let API_BASE = ""; // e.g. "https://api.autoapply-makwandecareers.co.za"

  const $ = (sel) => document.querySelector(sel);
  const jobsListEl = $("#jobsList");
  const emptyStateEl = $("#emptyState");
  const locationFilter = $("#locationFilter");
  const companyFilter = $("#companyFilter");
  const remoteOnly = $("#remoteOnly");
  const searchInput = $("#searchInput");

  // Seed a few sample jobs on first visit
  const SEED = [
    {
      id: crypto.randomUUID(), title: "Data Analyst", company: "Makwande Careers",
      location: "Johannesburg", country: "South Africa", remote: false,
      description: "Analyze job market data and deliver insights to product.",
      apply_url: "https://example.com/apply/1", closing_date: ""
    },
    {
      id: crypto.randomUUID(), title: "Frontend Engineer", company: "AutoApply",
      location: "Cape Town", country: "South Africa", remote: true,
      description: "Build delightful UI for our Auto Apply web app.",
      apply_url: "https://example.com/apply/2", closing_date: ""
    },
    {
      id: crypto.randomUUID(), title: "Recruitment Consultant", company: "Makwande Careers",
      location: "Durban", country: "South Africa", remote: false,
      description: "Source candidates and manage client relationships.",
      apply_url: "https://example.com/apply/3", closing_date: ""
    }
  ];

  function getJobs() {
    const raw = localStorage.getItem("jobs");
    if (!raw) {
      localStorage.setItem("jobs", JSON.stringify(SEED));
      return SEED.slice();
    }
    try { return JSON.parse(raw); } catch { return []; }
  }

  function saveJobs(list) {
    localStorage.setItem("jobs", JSON.stringify(list));
  }

  function unique(list, key) {
    return [...new Set(list.map(x => (x[key] || "").trim()).filter(Boolean))].sort();
  }

  function renderFilters(jobs) {
    const locs = unique(jobs, "location");
    const comps = unique(jobs, "company");
    locationFilter.innerHTML = `<option value="">All</option>` + locs.map(v=>`<option>${v}</option>`).join("");
    companyFilter.innerHTML = `<option value="">All</option>` + comps.map(v=>`<option>${v}</option>`).join("");
  }

  function jobMatchesFilters(job) {
    const q = searchInput.value.toLowerCase().trim();
    const loc = locationFilter.value;
    const comp = companyFilter.value;
    const remote = remoteOnly.checked;

    if (q) {
      const hay = `${job.title} ${job.company} ${job.location} ${job.country} ${job.description}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (loc && job.location !== loc) return false;
    if (comp && job.company !== comp) return false;
    if (remote && !job.remote) return false;
    return true;
  }

  function renderJobs() {
    const jobs = getJobs();
    const filtered = jobs.filter(jobMatchesFilters);

    jobsListEl.innerHTML = "";
    if (!filtered.length) {
      emptyStateEl.classList.remove("d-none");
      return;
    }
    emptyStateEl.classList.add("d-none");

    for (const job of filtered) {
      const badge = job.remote ? `<span class="badge text-bg-success ms-2">Remote</span>` : "";
      const closing = job.closing_date ? `<span class="small text-muted"> • Closes ${job.closing_date}</span>` : "";
      const card = document.createElement("div");
      card.className = "col-12";
      card.innerHTML = `
        <div class="card job-card border-0 shadow-sm">
          <div class="card-body d-flex flex-column flex-md-row justify-content-between">
            <div class="me-3">
              <h5 class="mb-1">${job.title} ${badge}</h5>
              <div class="text-muted mb-2">${job.company} • ${job.location}${closing}</div>
              <p class="mb-0">${(job.description || "").slice(0,220)}${job.description.length>220?"…":""}</p>
            </div>
            <div class="text-md-end mt-3 mt-md-0">
              <a class="btn btn-primary" target="_blank" rel="noopener" href="${job.apply_url}">Apply</a>
            </div>
          </div>
        </div>`;
      jobsListEl.appendChild(card);
    }
  }

  // Filters live-update
  [searchInput, locationFilter, companyFilter, remoteOnly].forEach(el => el.addEventListener("input", renderJobs));

  // Add Job form
  $("#addJobForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const job = {
      id: crypto.randomUUID(),
      title: fd.get("title").trim(),
      company: fd.get("company").trim(),
      location: fd.get("location").trim(),
      country: fd.get("country").trim(),
      remote: !!fd.get("remote"),
      closing_date: fd.get("closing_date") || "",
      apply_url: fd.get("apply_url").trim(),
      description: fd.get("description").trim()
    };

    // Save locally (works immediately)
    const list = getJobs();
    list.unshift(job);
    saveJobs(list);
    renderFilters(list);
    renderJobs();

    // Optional: try POST to backend if provided
    const modalApi = document.getElementById("apiBase").value.trim();
    const apiBase = modalApi || API_BASE;
    const apiKey = document.getElementById("apiKey").value.trim();
    if (apiBase) {
      try {
        await fetch(`${apiBase.replace(/\/$/,"")}/api/jobs`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(apiKey ? {"X-API-Key": apiKey} : {})
          },
          body: JSON.stringify(job)
        });
      } catch (err) {
        console.warn("POST to backend failed (ignored):", err);
      }
    }

    // close modal + reset
    const modalEl = document.getElementById('addJobModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
    e.target.reset();
  });

  // Init
  document.addEventListener("DOMContentLoaded", () => {
    const jobs = getJobs();
    renderFilters(jobs);
    renderJobs();
  });
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
