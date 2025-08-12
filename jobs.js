<script src="/static/js/main.js"></script>

jobs.js

async function fetchJobs(q = "") {
  const qs = q ? ?q=${encodeURIComponent(q)} : "";
  try {
    const res = await fetch(${API_BASE}/api/jobs${qs}, {
      headers: { ...authHeaders() }
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const msg = (data && (data.detail || data.message)) || "Failed to fetch jobs";
      return { ok: false, message: msg };
    }
    // Expect: array of jobs
    return { ok: true, data: Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : []) };
  } catch {
    return { ok: false, message: "Network error" };
  }
}
