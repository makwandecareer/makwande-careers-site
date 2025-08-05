// main.js
const API_URL = 'https://autoapplyapp.onrender.com/api/jobs';

async function fetchJobs() {
    const response = await fetch(API_URL);
    const jobs = await response.json();
    displayJobs(jobs);
}

function displayJobs(jobs) {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = '';

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        jobCard.innerHTML = `
            <h3>${job.title}</h3>
            <p><strong>Company:</strong> ${job.company}</p>
            <p><strong>Location:</strong> ${job.location}</p>
            <p><strong>Score:</strong> ${job.match_score}%</p>
            <p>${job.description}</p>
        `;
        jobList.appendChild(jobCard);
    });
}

document.addEventListener('DOMContentLoaded', fetchJobs);


