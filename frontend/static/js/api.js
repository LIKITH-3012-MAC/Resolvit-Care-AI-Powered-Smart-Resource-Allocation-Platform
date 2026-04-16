/**
 * Smart Resource Allocation — API Client
 * Unified API layer: Single Flask backend handles both auth + data.
 * 
 * DEPLOYMENT:
 *  - Frontend (UI): Served via Flask Templates (On Render)
 *  - Backend (Brain): Flask API + Auth (On Render)
 *  - Database: PostgreSQL
 */

// ──── UNIFIED API CONFIG ────
// Since the Flask backend now serves the UI via templates, we use relative paths.
// Point to the remote Render backend when deployed on Vercel
const BACKEND_DOMAIN = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://resolvit-care-ai-powered-smart-resource-allocation-naoaaoakp.vercel.app/';

const API_BASE_URL = `${BACKEND_DOMAIN}/api`;
const AUTH_BASE_URL = `${BACKEND_DOMAIN}/auth`;

class ApiClient {
  constructor() {
    this.accessToken = localStorage.getItem('accessToken');
  }

  get headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.accessToken) h['Authorization'] = `Bearer ${this.accessToken}`;
    return h;
  }

  setToken(token) { this.accessToken = token; localStorage.setItem('accessToken', token); }
  clearToken() { this.accessToken = null; localStorage.removeItem('accessToken'); localStorage.removeItem('user'); }
  getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } }
  setUser(user) { localStorage.setItem('user', JSON.stringify(user)); }
  isLoggedIn() { return !!this.accessToken; }

  async request(url, options = {}) {
    try {
      const res = await fetch(url, { headers: this.headers, ...options });

      // Handle non-JSON responses
      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        return {};
      }

      const data = await res.json();

      if (res.status === 401) {
        // Try token refresh
        const refreshed = await this.refresh();
        if (refreshed) {
          return (await fetch(url, { headers: this.headers, ...options })).json();
        }
        this.clearToken();
        window.location.href = '/login';
        throw new Error('Session expired');
      }

      if (!res.ok) throw new Error(data.error || data.detail || 'Request failed');
      return data;
    } catch (err) {
      if (err.message === 'Session expired') throw err;
      console.error('API Error:', err);
      throw err;
    }
  }

  // ── Auth (Unified Flask backend, /auth prefix) ──
  async requestOtp(email) {
    const res = await fetch(`${AUTH_BASE_URL}/request-signup-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.error || 'Failed to send OTP');
    return data;
  }

  async verifyOtp(email, otp) {
    const res = await fetch(`${AUTH_BASE_URL}/verify-signup-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.error || 'Verification failed');
    return data;
  }

  async register(data) {
    const res = await fetch(`${AUTH_BASE_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const r = await res.json();
    if (!res.ok) throw new Error(r.detail || r.error || 'Registration failed');
    if (r.accessToken) { this.setToken(r.accessToken); this.setUser(r.user); }
    return r;
  }

  async login(email, password) {
    const res = await fetch(`${AUTH_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const r = await res.json();
    if (!res.ok) throw new Error(r.detail || r.error || 'Login failed');
    if (r.accessToken) { this.setToken(r.accessToken); this.setUser(r.user); }
    return r;
  }

  async refresh() {
    try {
      const res = await fetch(`${AUTH_BASE_URL}/refresh`, {
        method: 'POST',
        headers: this.headers,
      });
      const r = await res.json();
      if (r.accessToken) { this.setToken(r.accessToken); return true; }
      return false;
    } catch { return false; }
  }

  async logout() {
    try { await fetch(`${AUTH_BASE_URL}/logout`, { method: 'POST', headers: this.headers }); } catch { }
    this.clearToken();
    // If Auth0 is available, use its logout for full session clear
    if (typeof logoutAuth0 === 'function') {
      logoutAuth0();
      return;
    }
    window.location.href = '/login.html';
  }

  async loginWithAuth0Token(auth0Token, userInfo = null) {
    // Try JWT callback first
    try {
      const res = await fetch(`${AUTH_BASE_URL}/auth0-callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: auth0Token })
      });
      if (res.ok) {
        const r = await res.json();
        if (r.accessToken) { this.setToken(r.accessToken); this.setUser(r.user); }
        return r;
      }
    } catch { }
    // Fallback: userinfo endpoint
    const res = await fetch(`${AUTH_BASE_URL}/auth0-userinfo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ access_token: auth0Token, user_info: userInfo })
    });
    const r = await res.json();
    if (!res.ok) throw new Error(r.detail || 'Auth0 login failed');
    if (r.accessToken) { this.setToken(r.accessToken); this.setUser(r.user); }
    return r;
  }

  async forgotPassword(email) {
    const res = await fetch(`${AUTH_BASE_URL}/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return res.json();
  }

  async validateResetToken(token, email) {
    return (await fetch(`${AUTH_BASE_URL}/validate-reset-token?token=${token}&email=${encodeURIComponent(email)}`)).json();
  }

  async resetPassword(token, email, password) {
    const res = await fetch(`${AUTH_BASE_URL}/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, email, password })
    });
    return res.json();
  }

  // ── Reports ──
  async getReports(p = {}) { return this.request(`${API_BASE_URL}/reports?${new URLSearchParams(p)}`); }
  async getReport(id) { return this.request(`${API_BASE_URL}/reports/${id}`); }
  async createReport(data) { return this.request(`${API_BASE_URL}/reports`, { method: 'POST', body: JSON.stringify(data) }); }

  // ── Volunteers ──
  async getVolunteers(p = {}) { return this.request(`${API_BASE_URL}/volunteers?${new URLSearchParams(p)}`); }
  async matchVolunteers(p) { return this.request(`${API_BASE_URL}/volunteers/match?${new URLSearchParams(p)}`, { method: 'POST' }); }

  // ── Tasks ──
  async getTasks(p = {}) { return this.request(`${API_BASE_URL}/tasks?${new URLSearchParams(p)}`); }
  async updateTask(id, data) { return this.request(`${API_BASE_URL}/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async assignTask(taskId, volId) { return this.request(`${API_BASE_URL}/tasks/${taskId}/assign/${volId}`, { method: 'POST' }); }

  // ── Analytics ──
  async getDashboard() { return this.request(`${API_BASE_URL}/analytics/dashboard`); }
  async getCategories() { return this.request(`${API_BASE_URL}/analytics/categories`); }
  async getPriorities() { return this.request(`${API_BASE_URL}/analytics/priorities`); }
  async getTimeline(d = 30) { return this.request(`${API_BASE_URL}/analytics/timeline?days=${d}`); }
  async getVolunteerStats() { return this.request(`${API_BASE_URL}/analytics/volunteers/stats`); }
  async getImpact() { return this.request(`${API_BASE_URL}/analytics/impact`); }

  // ── Maps ──
  async getMapReports(p = {}) { return this.request(`${API_BASE_URL}/maps/reports?${new URLSearchParams(p)}`); }
  async getMapVolunteers() { return this.request(`${API_BASE_URL}/maps/volunteers`); }
  async getHotspots(k = 4) { return this.request(`${API_BASE_URL}/maps/hotspots?k=${k}`); }
  async getHeatmap() { return this.request(`${API_BASE_URL}/maps/heatmap`); }

  // ── Resources ──
  async getResources(p = {}) { return this.request(`${API_BASE_URL}/resources?${new URLSearchParams(p)}`); }
}

window.api = new ApiClient();
