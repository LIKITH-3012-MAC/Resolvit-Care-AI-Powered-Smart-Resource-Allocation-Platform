/**
 * Theme Toggle — Dark/Light mode with persistence
 */

(function() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);

  window.toggleTheme = function() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    
    const toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) toggleBtn.classList.toggle('light', next === 'light');
  };
})();

/**
 * Toast notifications
 */
window.showToast = function(message, type = 'info', duration = 4000) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
};

/**
 * Number animation
 */
window.animateNumber = function(el, target, duration = 1200) {
  const start = 0;
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (target - start) * eased);
    
    el.textContent = current.toLocaleString();
    
    if (progress < 1) requestAnimationFrame(update);
  }
  
  requestAnimationFrame(update);
};

/**
 * Format date/time
 */
window.formatDate = function(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};

window.formatTime = function(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
};

window.timeAgo = function(dateStr) {
  const d = new Date(dateStr);
  const now = new Date();
  const diff = (now - d) / 1000;
  
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return formatDate(dateStr);
};

/**
 * Priority badge HTML
 */
window.priorityBadge = function(level) {
  const l = (level || 'medium').toLowerCase();
  return `<span class="badge badge-${l}"><span class="badge-dot"></span>${l}</span>`;
};

/**
 * Mobile menu toggle
 */
window.toggleSidebar = function() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) sidebar.classList.toggle('open');
};
