/* ════════════════════════════════════════════════════════════════════
   ASMaP — Shared Frontend Utilities
   api.js  v1.0
════════════════════════════════════════════════════════════════════ */

/* ── CONFIGURATION ───────────────────────────────────────────────────
   Set this to your backend URL when deploying.
   During local development it defaults to localhost:5000.
   Example production: 'https://asmap-api.onrender.com'
──────────────────────────────────────────────────────────────────── */
const API_BASE = window.API_BASE || 'https://asmap-backend.onrender.com/api';

/* ══════════════════════════════════════════════════════════════════
   AUTH
══════════════════════════════════════════════════════════════════ */
const Auth = {
  key:      'asmap_token',
  userKey:  'asmap_user',

  save(token, user) {
    localStorage.setItem(this.key,     token);
    localStorage.setItem(this.userKey, JSON.stringify(user));
  },

  token()  { return localStorage.getItem(this.key); },
  user()   { try { return JSON.parse(localStorage.getItem(this.userKey)); } catch { return null; } },
  role()   { return this.user()?.role || null; },

  logout() {
    localStorage.removeItem(this.key);
    localStorage.removeItem(this.userKey);
    window.location.href = 'login.html';
  },

  /** Call on every protected page load. Returns false + redirects if not authed. */
  require() {
    if (!this.token()) { window.location.href = 'login.html'; return false; }
    return true;
  },

  /** Require a specific role (or array of roles). */
  requireRole(role) {
    if (!this.require()) return false;
    const roles = Array.isArray(role) ? role : [role];
    if (!roles.includes(this.role())) {
      alert('Access denied. You do not have permission to view this page.');
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },
};

/* ══════════════════════════════════════════════════════════════════
   API CLIENT
══════════════════════════════════════════════════════════════════ */
const Api = {
  _headers(extra) {
    const h = { 'Content-Type': 'application/json' };
    const t = Auth.token();
    if (t) h['Authorization'] = `Bearer ${t}`;
    return { ...h, ...extra };
  },

  async _handle(res) {
    if (res.status === 401) { Auth.logout(); throw new Error('Session expired. Please log in again.'); }
    let body;
    const ct = res.headers.get('Content-Type') || '';
    if (ct.includes('application/json')) {
      body = await res.json();
    } else {
      // Binary response (Excel download etc.)
      const blob = await res.blob();
      if (!res.ok) throw new Error('Download failed');
      return blob;
    }
    if (!res.ok) throw new Error(body?.error || body?.message || `HTTP ${res.status}`);
    return body;
  },

  async get(path) {
    const r = await fetch(`${API_BASE}${path}`, { headers: this._headers() });
    return this._handle(r);
  },

  async post(path, data) {
    const r = await fetch(`${API_BASE}${path}`, {
      method: 'POST', headers: this._headers(), body: JSON.stringify(data)
    });
    return this._handle(r);
  },

  async put(path, data) {
    const r = await fetch(`${API_BASE}${path}`, {
      method: 'PUT', headers: this._headers(), body: JSON.stringify(data)
    });
    return this._handle(r);
  },

  async del(path) {
    const r = await fetch(`${API_BASE}${path}`, {
      method: 'DELETE', headers: this._headers()
    });
    return this._handle(r);
  },

  async upload(path, formData) {
    const headers = {};
    const t = Auth.token();
    if (t) headers['Authorization'] = `Bearer ${t}`;
    const r = await fetch(`${API_BASE}${path}`, { method: 'POST', headers, body: formData });
    return this._handle(r);
  },
};

/* ══════════════════════════════════════════════════════════════════
   TOAST NOTIFICATIONS
══════════════════════════════════════════════════════════════════ */
const Toast = {
  _container() {
    let el = document.getElementById('toast-container');
    if (!el) { el = document.createElement('div'); el.id = 'toast-container'; document.body.appendChild(el); }
    return el;
  },
  _show(msg, type) {
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    const icon = { success: '✓', error: '✕', info: 'ℹ' }[type] || '•';
    t.innerHTML = `<span style="font-size:1.1rem">${icon}</span><span>${msg}</span>`;
    this._container().appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(30px)';
                       t.style.transition = 'all 0.3s'; setTimeout(() => t.remove(), 320); }, 3800);
  },
  success(msg) { this._show(msg, 'success'); },
  error(msg)   { this._show(msg, 'error'); },
  info(msg)    { this._show(msg, 'info'); },
};

/* ══════════════════════════════════════════════════════════════════
   UI HELPERS
══════════════════════════════════════════════════════════════════ */
const UI = {

  /* ── Sections ────────────────────────────────────────────────── */
  switchSection(name) {
    document.querySelectorAll('.section-view').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(`section-${name}`);
    if (el) el.classList.add('active');
    window.scrollTo(0, 0);
  },

  /* ── Modals ──────────────────────────────────────────────────── */
  openModal(id)  { const m = document.getElementById(id); if (m) m.classList.add('open'); },
  closeModal(id) { const m = document.getElementById(id); if (m) m.classList.remove('open'); },

  /* ── Sidebar / hamburger ──────────────────────────────────────── */
  initHamburger() {
    const btn  = document.getElementById('hamburger');
    const side = document.getElementById('sidebar');
    if (!btn || !side) return;
    btn.addEventListener('click', () => side.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (side.classList.contains('open') && !side.contains(e.target) && e.target !== btn)
        side.classList.remove('open');
    });
  },

  /* ── User display ────────────────────────────────────────────── */
  initUserDisplay() {
    const user = Auth.user();
    if (!user) return;
    const el = document.getElementById('sidebar-user-name');
    if (el) el.textContent = user.full_name || user.username;
    const re = document.getElementById('sidebar-user-role');
    if (re) re.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
  },

  /* ── School branding ─────────────────────────────────────────── */
  async loadSchoolBranding() {
    try {
      const s = await Api.get('/admin/settings/public').catch(() => null);
      if (!s) return;

      // Set all school name elements
      document.querySelectorAll('[data-school-name]').forEach(el => {
        el.textContent = s.school_name || 'Your School';
      });
      document.querySelectorAll('[data-school-motto]').forEach(el => {
        el.textContent = s.school_motto || '';
      });

      // School logo/crest
      if (s.school_logo) {
        document.querySelectorAll('[data-school-logo]').forEach(el => {
          if (el.tagName === 'IMG') el.src = s.school_logo;
        });
      }
    } catch (e) { /* branding is cosmetic, don't block on failure */ }
  },

  async loadFullBranding() {
    try {
      const s = await Api.get('/admin/settings');
      if (!s) return;
      document.querySelectorAll('[data-school-name]').forEach(el => el.textContent = s.school_name || '');
      document.querySelectorAll('[data-school-motto]').forEach(el => el.textContent = s.school_motto || '');
      if (s.school_logo) {
        document.querySelectorAll('[data-school-logo]').forEach(el => {
          if (el.tagName === 'IMG') el.src = s.school_logo;
        });
      }
      return s;
    } catch(e) { return null; }
  },

  /* ── Select population ───────────────────────────────────────── */
  populateSelect(id, items, valKey, labelKey, placeholder) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
    items.forEach(item => {
      const o = document.createElement('option');
      o.value       = item[valKey];
      o.textContent = item[labelKey] || item[valKey];
      el.appendChild(o);
    });
  },

  /* ── Currency formatting (GHS) ───────────────────────────────── */
  currency(val) {
    const n = parseFloat(val) || 0;
    return 'GHS\u00a0' + n.toLocaleString('en-GH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  },

  /* ── Date formatting ─────────────────────────────────────────── */
  date(val) {
    if (!val) return '—';
    try {
      const d = new Date(val);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch { return val; }
  },

  /* ── Badge helper ────────────────────────────────────────────── */
  badge(text, type) {
    return `<span class="badge badge-${type || 'grey'}">${text}</span>`;
  },

  /* ── Session type badge ──────────────────────────────────────── */
  sessionBadge(type) {
    const cls = type === 'Extended' ? 'session-extended' : 'session-normal';
    return `<span class="${cls}">${type}</span>`;
  },

  /* ── On-time badge ───────────────────────────────────────────── */
  onTimeBadge(val) {
    if (val === null || val === undefined) return '<span class="unmarked">—</span>';
    return val
      ? '<span class="on-time">✓ On time</span>'
      : '<span class="late">✗ Late</span>';
  },

  /* ── Loading / empty states ──────────────────────────────────── */
  loading() { return '<div class="loading-overlay"><div class="spinner"></div></div>'; },
  empty(msg) { return `<div class="empty-state">${msg || 'No records found'}</div>`; },

  /* ── Download blob ───────────────────────────────────────────── */
  downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a   = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  },

  /* ── Teacher search dropdown ─────────────────────────────────── */
  initTeacherSearch({ inputId, hiddenId, dropdownId, teachers }) {
    const input    = document.getElementById(inputId);
    const hidden   = document.getElementById(hiddenId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    function render(q) {
      const fl = (q ? teachers.filter(t => t.teacher_name.toLowerCase().includes(q.toLowerCase())) : teachers).slice(0, 40);
      dropdown.innerHTML = fl.length
        ? fl.map(t => `<div class="dropdown-option" data-id="${t.id}" data-name="${t.teacher_name}">
            ${t.teacher_name}${t.subject ? `<span style="color:var(--text-3);font-size:0.78rem;margin-left:6px">· ${t.subject}</span>` : ''}
           </div>`).join('')
        : `<div class="dropdown-option" style="color:var(--text-3)">No match found</div>`;

      dropdown.querySelectorAll('[data-id]').forEach(el => {
        el.addEventListener('mousedown', e => {
          e.preventDefault();
          input.value  = el.dataset.name;
          if (hidden) hidden.value = el.dataset.id;
          dropdown.classList.remove('open');
          input.dispatchEvent(new Event('teacher-selected'));
        });
      });
      dropdown.classList.toggle('open', fl.length > 0);
    }

    input.addEventListener('input',  () => render(input.value));
    input.addEventListener('focus',  () => render(input.value));
    input.addEventListener('blur',   () => setTimeout(() => dropdown.classList.remove('open'), 150));
    document.addEventListener('click', e => {
      if (!input.closest('.search-dropdown')?.contains(e.target))
        dropdown.classList.remove('open');
    });
  },
};

/* ══════════════════════════════════════════════════════════════════
   NAVIGATION HELPER
══════════════════════════════════════════════════════════════════ */
function makeNav(sectionLoaded, loaderMap) {
  return function go(name) {
    UI.switchSection(name);
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll(`[data-section="${name}"]`).forEach(n => n.classList.add('active'));
    const titleEl = document.getElementById('topbar-title');
    if (titleEl) {
      const txt = document.querySelector(`[data-section="${name}"]`)?.textContent?.trim();
      titleEl.textContent = txt || name;
    }
    if (!sectionLoaded[name] && loaderMap[name]) {
      sectionLoaded[name] = true;
      loaderMap[name]();
    }
  };
}

/* Close modal on overlay click */
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('open');
});
