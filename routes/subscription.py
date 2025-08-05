// main.js - Absolute URL version for Vercel + Render integration

// ✅ Absolute URL for Render backend
const API_BASE_URL = 'https://autoapply-api.onrender.com';

async function fetchMatchedJobs() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/matched_jobs`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('job-list').innerHTML = '<p>Error loading jobs.</p>';
    }
}

function displayJobs(jobs) {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = '';

    if (jobs.length === 0) {
        jobList.innerHTML = '<p>No matched jobs found.</p>';
        return;
    }

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.classList.add('job-card');

        jobCard.innerHTML = `
            <h3>${job.title}</h3>
            <p><strong>Company:</strong> ${job.company}</p>
            <p><strong>Location:</strong> ${job.location}</p>
            <p><strong>Score:</strong> ${job.match_score}%</p>
            <a href="${job.url}" target="_blank">View Job</a>
        `;

        jobList.appendChild(jobCard);
    });
}

// Load jobs on page load
window.onload = fetchMatchedJobs;


