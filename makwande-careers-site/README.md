# Makwande Careers Site (Frontend)

A polished, green-themed static frontend integrated with your FastAPI backend.

## Configure
- Edit `js/config.js` and set:
  ```js
  window.API_BASE = "https://<your-backend-on-render>";
  ```
- In `js/pay.js`, replace Paystack public key.

## Deploy (Static Site)
- Upload the ZIP to Render Static Sites (or Vercel/Netlify).

## Monorepo Deploy (Backend + Frontend)
- Put this folder at repo root as `makwande-careers-site/`.
- Place `render.yaml` at repo root with `staticPublishPath: makwande-careers-site`.
- Connect repo to Render → it will create both services.

## Pages
- `/login.html`, `/signup.html`
- `/jobs.html`, `/autoapply.html`
- `/revamp.html`, `/cover_letter.html`
- `/recruiter.html`, `/employer.html`
- `/dashboard.html`, `/pay.html`



### Preview
![Preview](assets/img/preview.gif)
