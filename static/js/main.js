// ==============================
// ✅ LIVE: Job Board Connected
// ==============================
fetch('https://autoapply-api.onrender.com/api/jobs')
  .then(response => response.json())
  .then(data => {
    let jobsHtml = '';
    data.forEach(job => {
      jobsHtml += `
        <div class="job-card">
          <h3>${job.title}</h3>
          <p><strong>Company:</strong> ${job.company}</p>
          <p><strong>Location:</strong> ${job.location}</p>
          <p><strong>Score:</strong> ${job.match_score}%</p>
          <a href="${job.link}" target="_blank">View Job</a>
        </div>
        <hr/>
      `;
    });
    document.getElementById("job-list").innerHTML = jobsHtml;
  })
  .catch(error => {
    console.error('Error loading jobs:', error);
    document.getElementById("job-list").innerHTML = `
      <p style="text-align:center; color: red;">
        🚫 Unable to load jobs at this moment. Please try again later.
      </p>`;
  }); n n 



