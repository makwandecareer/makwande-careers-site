# Data Protection Policy (Internal)

## Purpose
To define technical and organisational measures to safeguard personal information under POPIA.

## Roles
- Information Officer: **{{INFO_OFFICER_NAME}}** (overall accountability)
- Security Lead: **{{SECURITY_LEAD_NAME}}**
- Engineering Lead: **{{ENG_LEAD_NAME}}**

## Measures
- Encryption in transit (HTTPS/TLS) and at rest (where supported).
- Access control: least privilege, role-based, unique accounts, MFA for admins.
- Logging & monitoring: auth events, data exports, admin actions.
- Malware scanning on uploads (CVs).
- Vendor due diligence and DPAs with operators.
- Regular backups and tested restores.

## Incident Response
Follow `/policies/incident-response-plan.md`.

## Data Subject Requests
Route to **{{CONTACT_EMAIL}}**; respond without undue delay.
