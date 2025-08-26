/* config.js
   Global app config + tiny API helper.
   - Picks API base in this order:
     1) ?api=https://custom (persisted)
     2) localStorage.API_BASE
     3) default: localhost for dev, DEFAULT_PROD for prod
   - Exposes: APP_CONFIG + apiFetch on window
*/

(function (w) {
  'use strict';

  const DEFAULT_LOCAL = 'http://127.0.0.1:8000';
  const DEFAULT_PROD  = 'https://autoapplyapp.onrender.com'; // 
 

  const LS = w.localStorage;
  const KEYS = {
    API_BASE: 'API_BASE',
    AUTH: 'AUTH_TOKEN',
  };

  // Allow ?api=https://foo to override (and persist)
  (() => {
    const apiFromURL = new URLSearchParams(w.location.search).get('api');
    if (apiFromURL) {
      try { setApiBase(apiFromURL); } catch (_) { /* ignore bad values */ }
    }
  })();

  function inferDefaultApi() {
    const host = w.location.hostname;
    const isLocal = /^(localhost|127\.0\.0\.1|0\.0\.0\.0)$/i.test(host);
    return isLocal ? DEFAULT_LOCAL : DEFAULT_PROD;
  }

  function normalizeBase(url) {
    if (!/^https?:\/\//i.test(url)) {
      throw new Error('API base must start with http:// or https://');
    }
    return url.replace(/\/+$/, '');
  }

  let API_BASE = LS.getItem(KEYS.API_BASE) || inferDefaultApi();
  API_BASE = normalizeBase(API_BASE);

  function setApiBase(url) {
    API_BASE = normalizeBase(url);
    LS.setItem(KEYS.API_BASE, API_BASE);
    w.APP_CONFIG.API_BASE = API_BASE;
    return API_BASE;
  }
  function getApiBase() { return API_BASE; }
  function clearApiBase() {
    LS.removeItem(KEYS.API_BASE);
    API_BASE = normalizeBase(inferDefaultApi());
    w.APP_CONFIG.API_BASE = API_BASE;
    return API_BASE;
  }

  function setAuthToken(token) {
    if (token) LS.setItem(KEYS.AUTH, token);
    else LS.removeItem(KEYS.AUTH);
  }
  function getAuthToken() { return LS.getItem(KEYS.AUTH); }
  function clearAuthToken() { LS.removeItem(KEYS.AUTH); }

  function buildHeaders(extra = {}, json = true) {
    const h = { ...extra };
    const t = getAuthToken();
    if (t) h['Authorization'] = 'Bearer ' + t;
    if (json && !('Content-Type' in h) && !(extra instanceof FormData)) {
      h['Content-Type'] = 'application/json';
    }
    return h;
  }

  async function apiFetch(path, opts = {}) {
    const {
      method = 'GET',
      headers = {},
      body = null,
      json = true,  // when true, JSON.stringify body and parse JSON response
    } = opts;

    const base = getApiBase().replace(/\/+$/, '');
    const url = /^https?:\/\//i.test(path) ? path : base + (path.startsWith('/') ? path : '/' + path);

    const init = { method, headers: buildHeaders(headers, json) };
    if (body != null) {
      init.body = (json && !(body instanceof FormData)) ? JSON.stringify(body) : body;
    }

    const res = await fetch(url, init);
    const raw = await res.text();
    let data = null;
    try { data = raw ? JSON.parse(raw) : null; } catch { data = raw; }

    if (!res.ok) {
      const msg = (data && (data.detail || data.message)) || res.statusText || 'Request failed';
      const err = new Error(msg);
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  // Public API
  w.APP_CONFIG = {
    API_BASE,
    DEFAULT_LOCAL,
    DEFAULT_PROD,
    STORAGE_KEYS: { ...KEYS },
    // API base controls
    setApiBase, getApiBase, clearApiBase,
    // Auth token controls
    setAuthToken, getAuthToken, clearAuthToken,
    // Helpers
    buildHeaders,
    apiFetch, // also exposed separately below
  };

  // Convenience: window.apiFetch(...)
  w.apiFetch = apiFetch;

})(window);
