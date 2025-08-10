<script>
// ---- Auth token storage ----
const tokenKey = "aa_token";

function setToken(jwt) {
  localStorage.setItem(tokenKey, jwt);
}

function getToken() {
  return localStorage.getItem(tokenKey);
}

function clearToken() {
  localStorage.removeItem(tokenKey);
}

// ---- API helper (adds Authorization automatically) ----
async function api(path, { method = "GET", body, headers = {} } = {}) {
  const base = window._CONFIG_.API_BASE_URL.replace(/\/+$/, "");
  const url = ${base}${path.startsWith("/") ? "" : "/"}${path};

  const jwt = getToken();
  const h = { "Content-Type": "application/json", ...headers };
  if (jwt) h.Authorization = Bearer ${jwt};

  const res = await fetch(url, {
    method,
    headers: h,
    body: body ? JSON.stringify(body) : undefined,
  });

  // If unauthorized, kick back to login
  if (res.status === 401) {
    clearToken();
    if (!location.pathname.endsWith("index.html")) {
      location.href = "index.html";
    }
  }

  // Try json, fall back to text
  const text = await res.text();
  try { return { ok: res.ok, status: res.status, data: JSON.parse(text) }; }
  catch { return { ok: res.ok, status: res.status, data: text }; }
}

// ---- Route guards ----
function requireAuth() {
  if (!getToken()) location.href = "index.html";
}

</script>