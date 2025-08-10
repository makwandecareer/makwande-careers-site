// api.js
(function () {
    const BASE = window.CONFIG.API_BASE_URL;

    const TOKEN_KEY = "aa_token";

    function saveToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    }

    function getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    function clearToken() {
        localStorage.removeItem(TOKEN_KEY);
    }

    async function api(path, { method = "GET", body, auth = false } = {}) {
        const headers = { "Content-Type": "application/json" };
        if (auth) {
            const tok = getToken();
            if (tok) headers["Authorization"] = Bearer ${tok};
        }
        const res = await fetch(${BASE}${path}, {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined
        });

        let data;
        try { 
            data = await res.json(); 
        } catch { 
            data = null; 
        }

        if (!res.ok) {
            const msg = (data && (data.detail || data.message)) || HTTP ${res.status};
            throw new Error(msg);
        }
        return data;
    }

    async function signup(payload) {
        return api("/signup", { method: "POST", body: payload });
    }

    async function login(payload) {
        const data = await api("/login", { method: "POST", body: payload });
        if (data && data.access_token) saveToken(data.access_token);
        return data;
    }

    async function fetchJobs() {
        return api("/jobs", { auth: true });
    }

    window.AutoApply = {
        signup,
        login,
        fetchJobs,
        saveToken,
        getToken,
        clearToken
    };
})();