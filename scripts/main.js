// main.js

// ✅ Updated API URL to point to your Render backend
const API_URL = 'https://autoapply-api.onrender.com/api/jobs';

// Fetch job data from the backend API
async function fetchJobs() {
    try {
        const response = await fetch(API_URL);
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error('Error fetching jobs:', error);
        const jobList = document.getElementById('job-list');
        jobList.innerHTML = '<p style="color:red;">Error loading jobs. Please try again later.</p>';
    }
}

// Render job cards to the page
function displayJobs(jobs) {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = ''; // Clear previous content

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

// Call the function on page load
fetchJobs();




