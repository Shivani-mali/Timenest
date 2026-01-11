(() => {
  const API = window.location.origin + '/api';
  const TOKEN_KEY = 'timenest_token';

  async function jsonFetch(url, options = {}) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(url, { headers, ...options });
    let body = null;
    try { body = await res.json(); } catch (_) {}
    return { status: res.status, ok: res.ok, data: body };
  }

  async function login(email, password) {
    const res = await jsonFetch(`${API}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (res.ok && res.data?.access_token) setToken(res.data.access_token);
    return res;
  }

  async function register(email, password) {
    const res = await jsonFetch(`${API}/auth/register`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (res.ok && res.data?.access_token) setToken(res.data.access_token);
    return res;
  }

  async function me() {
    return jsonFetch(`${API}/auth/me`);
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }
  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }
  function logout() {
    localStorage.removeItem(TOKEN_KEY);
  }

  window.TimeNestAuth = { login, register, me, getToken, setToken, logout };
})();
