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

// --- FORCE add Profile + Public Profile links (idempotent, survives re-renders)
(function () {
  function addLinks() {
    const navWrap = document.querySelector('nav.nav-wrap');
    if (!navWrap) return;

    const slot =
      navWrap.querySelector('.ms-auto') ||
      navWrap.querySelector('.container-xxl') ||
      navWrap; // fallback

    // Top-level "Profile"
    if (!slot.querySelector('a[href="/candidate-profile.html"]')) {
      const a = document.createElement('a');
      a.className = 'text-decoration-none nav-link-lite';
      a.href = '/candidate-profile.html';
      a.textContent = 'Profile';
      slot.appendChild(a);
    }

    // "Public Profile" (prefer dropdown, else top-level)
    const menu = slot.querySelector('.dropdown-menu');
    if (menu) {
      if (!menu.querySelector('a[href="/public-profile.html"]')) {
        const li = document.createElement('li');
        li.innerHTML = '<a class="dropdown-item" href="/public-profile.html">Public Profile</a>';
        menu.appendChild(li);
      }
    } else if (!slot.querySelector('a[href="/public-profile.html"]')) {
      const a2 = document.createElement('a');
      a2.className = 'text-decoration-none nav-link-lite';
      a2.href = '/public-profile.html';
      a2.textContent = 'Public Profile';
      slot.appendChild(a2);
    }
  }

  const boot = () => { try { addLinks(); } catch {} };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  window.addEventListener('load', boot);

  // Re-run if anything rewrites the nav later
  const target = document.querySelector('nav.nav-wrap') || document.body;
  new MutationObserver(() => boot()).observe(target, { childList: true, subtree: true });
})();

// Put Profile links at the top of the "More" dropdown
document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('nav.nav-wrap .dropdown-menu');
  if (!menu) return;

  const has = (sel) => !!menu.querySelector(sel);
  if (!has('a[href="/candidate-profile.html"]') && !has('a[href="/public-profile.html"]')) {
    menu.insertAdjacentHTML('afterbegin', `
      <li><a class="dropdown-item" href="/candidate-profile.html">Profile</a></li>
      <li><a class="dropdown-item" href="/public-profile.html">Public Profile</a></li>
      <li><hr class="dropdown-divider"></li>
    `);
  }
});

