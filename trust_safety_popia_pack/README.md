# Trust & Safety + POPIA Starter Pack
**Date:** 2025-08-26

This pack gives you:
- POPIA-ready policy templates (Privacy, Terms, Cookies, Data Protection).
- Trust & Safety docs to fight scams (Verification SOP, Anti-Scam checklist, Reporting).
- Backend FastAPI code: security headers, rate limiting hooks, moderation endpoints, validation, malware scan stub.
- Frontend: Report button to flag suspicious jobs.
- SQL schema for verified employers and moderation queue.

> Replace **{COMPANY_NAME}** and **{CONTACT_EMAIL}** etc. Site name: **Makwande Careers / Auto Apply App**.

## Quick Integration
1. **Policies**: Publish `/policies/*.md` as pages (Privacy/Terms/Cookies/Report).
2. **Backend (FastAPI)**:
   - Include `backend/security/security_headers.py` and add `add_security_headers(app)`.
   - Configure CORS in your `main.py`.
   - Mount `backend/routers/trust_safety.py` with `app.include_router(trust_safety.router)`.
   - Optional: enable rate limiting (`backend/security/rate_limit.py`) once dependency installed.
   - Add `moderation_rules.py` and call from your job ingestion/matching to auto-flag.
3. **DB**: Run `sql/jobs_verification.sql` to add tables/columns if needed.
4. **Frontend**: Include `frontend/components/report-button.js` on the jobs page; pass job data attributes.
5. **Go-Live**: Update contacts and retention periods in policy docs.

## Dependencies (optional)
- `pip install slowapi` for rate limiting
- `pip install python-clamd` (and system clamav) for malware scanning
