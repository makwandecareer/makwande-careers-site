// --- Ensure Profile links exist in nav (runs after DOM is ready)
(function () {
  const run = () => {
    const nav = document.querySelector('nav.nav-wrap .ms-auto');
    if (!nav) return;

    // Add top-level "Profile"
    if (!nav.querySelector('a[href="/candidate-profile.html"]')) {
      const a = document.createElement('a');
      a.className = 'text-decoration-none nav-link-lite';
      a.href = '/candidate-profile.html';
      a.textContent = 'Profile';
      nav.insertBefore(a, nav.firstChild); // put it near the start
    }

    // Add "Public Profile" into dropdown if present
    const menu = nav.querySelector('.dropdown-menu');
    if (menu && !menu.querySelector('a[href="/public-profile.html"]')) {
      const li = document.createElement('li');
      li.innerHTML = '<a class="dropdown-item" href="/public-profile.html">Public Profile</a>';
      menu.appendChild(li);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { try { run(); } catch {} });
  } else {
    try { run(); } catch {}
  }
})();
