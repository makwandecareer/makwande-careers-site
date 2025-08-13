const TOKEN_KEY = "autoapply_token";

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function logout() {
  localStorage.removeItem(TOKEN_KEY);
}
function requireAuth() {
  if (!getToken()) window.location.href = "index.html";
}

async function login(email, password) {
  try {
    const res = await fetch(${API_BASE}/api/auth/login, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) return { ok: false, message: data.detail || "Invalid credentials" };
    // Expect { access_token, token_type }
    if (data.access_token) saveToken(data.access_token);
    return { ok: true };
  } catch (e) {
    return { ok: false, message: "Network error" };
  }
}

async function signup(payload) {
  try {
    const res = await fetch(${API_BASE}/api/auth/signup, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) return { ok: false, message: data.detail || "Sign-up failed" };
    return { ok: true };
  } catch {
    return { ok: false, message: "Network error" };
  }
}

function authHeaders() {
  const t = getToken();
  return t ? { Authorization: Bearer ${t} } : {};
}