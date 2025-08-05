// dashboard.js
const API_URL = 'https://autoapplyapp.onrender.com/api/dashboard';

async function loadDashboard() {
    const response = await fetch(API_URL);
    const data = await response.json();

    document.getElementById("status").innerText = `Subscription: ${data.subscription_status}`;
    document.getElementById("applications").innerHTML = data.applied_jobs.map(job => `
        <li>${job.title} at ${job.company} — ${job.status}</li>
    `).join('');
}

document.addEventListener('DOMContentLoaded', loadDashboard);
