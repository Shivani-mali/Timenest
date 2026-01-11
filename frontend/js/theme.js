// Theme toggle functionality
(() => {
  const THEME_KEY = 'timenest_theme';
  
  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 'dark';
  }
  
  function setTheme(theme) {
    localStorage.setItem(THEME_KEY, theme);
    document.documentElement.setAttribute('data-theme', theme);
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
  }
  
  function toggleTheme() {
    const current = getTheme();
    setTheme(current === 'dark' ? 'light' : 'dark');
  }
  
  // Initialize theme on page load
  setTheme(getTheme());
  
  // Attach event listener
  window.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.addEventListener('click', toggleTheme);
    }
  });
})();
