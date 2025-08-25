# Makwande Careers — Static Site

This folder contains the static frontend for AutoApply. It is designed to be deployed on Render as a **Static Site**.

## One rewrite rule (no CORS needed)
- **Source:** `/api/*`
- **Destination:** `https://autoapplyapp.onrender.com/api/*`
- **Action:** `Rewrite`

All frontend code uses **relative** calls (e.g., `fetch('/api/jobs')`).

## Pages
- Marketing: index, pricing, employers, recruiters, investors, partnerships, brand-collaborations
- Auth: login, signup
- App: jobs, revamp, cover_letter, dashboard, subscription, payment
- Recruiter/Employer: post-job, recruiter-dashboard, employer-dashboard
- Bursaries: bursaries, bursary-apply, admin-bursaries
- Learners/Universities: learners, universities

## Assets
- `/assets/img/logo.png`
- `/assets/img/africa-map.png`
- `/assets/css/style.css`
- `/assets/js/main.js`

## Notes
- Keep pages as real `.html` files (no SPA fallback). 
- All API endpoints are under `/api/*` and proxied to the backend service at Render.
- Update text and content as needed; layout uses Bootstrap 5.
