// 1-line API helper for all pages
window.fetchAPI = (p,o={}) => fetch('/api'+p,{credentials:'include',...o});

// Invisible dynamic nav (runs on every page)
function injectNav(){
  const c = document.querySelector('nav.nav-wrap .ms-auto');
  if (!c) return;

  c.innerHTML = ''; // clear anything there

  // main links
  const links = [
    ['Home','/index.html'], ['Jobs','/jobs.html'], ['Revamp CV','/revamp.html'],
    ['Cover Letter','/cover_letter.html'], ['Pricing','/pricing.html'],
    ['Dashboard','/dashboard.html']
  ];
  for (const [t,h] of links){
    const a = document.createElement('a');
    a.className = 'text-decoration-none nav-link-lite';
    a.href = h; a.textContent = t; c.appendChild(a);
  }

  // More dropdown (visible UI, but no raw code printed)
  const wrap = document.createElement('div');
  wrap.className = 'dropdown';
  wrap.innerHTML = `
    <a class="btn btn-soft dropdown-toggle rounded-pill" href="#" role="button" data-bs-toggle="dropdown">More</a>
    <ul class="dropdown-menu dropdown-menu-end">
      <li><h6 class="dropdown-header">More</h6></li>
      <li><a class="dropdown-item" href="/recruiter.html">Recruiter</a></li>
      <li><a class="dropdown-item" href="/recruiter-dashboard.html">Recruiter Dashboard</a></li>
      <li><a class="dropdown-item" href="/employer.html">Employers</a></li>
      <li><a class="dropdown-item" href="/employer-dashboard.html">Employer Dashboard</a></li>
      <li><a class="dropdown-item" href="/post-job.html">Post Job</a></li>
      <li><hr class="dropdown-divider"></li>
      <li><a class="dropdown-item" href="/bursaries.html">Bursaries</a></li>
      <li><a class="dropdown-item" href="/bursary-apply.html">Bursary Apply</a></li>
      <li><a class="dropdown-item" href="/admin-bursaries.html">Admin Bursaries</a></li>
      <li><a class="dropdown-item" href="/learners.html">Learners</a></li>
      <li><a class="dropdown-item" href="/universities.html">Universities</a></li>
      <li><hr class="dropdown-divider"></li>
      <li><a class="dropdown-item" href="/investors.html">Investors</a></li>
      <li><a class="dropdown-item" href="/partnerships.html">Partnerships</a></li>
      <li><a class="dropdown-item" href="/brand-collaborations.html">Brand Collaborations</a></li>
      <li><a class="dropdown-item" href="/marketing.html">Marketing</a></li>
      <li><a class="dropdown-item" href="/components.html">Components</a></li>
      <li><hr class="dropdown-divider"></li>
      <li><a class="dropdown-item" href="/sitemap.html">Sitemap</a></li>
    </ul>`;
  c.appendChild(wrap);
}

document.addEventListener('DOMContentLoaded', () => { try { injectNav(); } catch(e){} });
