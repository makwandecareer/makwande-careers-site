// main.js

// Load exclusions from localStorage
function getExclusions() {
  return (localStorage.getItem("excluded_companies") || "").toLowerCase().split(",");
}

// Save exclusions to localStorage and backend
function saveExclusions() {
  const exclusions = document.getElementById("exclude_companies").value;
  localStorage.setItem("excluded_companies", exclusions);
  fetch("https://your-backend-url.onrender.com/api/set_exclusions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exclusions: exclusions, user_email: localStorage.getItem("email") || "anonymous" })
  })
    .then(res => res.json())
    .then(data => alert("Exclusions saved successfully!"))
    .catch(err => console.error("Failed to save exclusions:", err));
}

// Function to apply for a job if it's not excluded
async function applyToJob(job) {
  const excluded = getExclusions();
  if (excluded.some(ex => job.company.toLowerCase().includes(ex.trim()))) {
    console.log(`❌ Skipping job at ${job.company} due to exclusion.`);
    return;
  }

  const response = await fetch("https://your-backend-url.onrender.com/api/apply_job", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_id: job.id,
      company: job.company,
      user_email: localStorage.getItem("email") || "anonymous"
    })
  });

  const result = await response.json();
  console.log(result.message);
}

// Navigation utilities
function goTo(page) {
  window.location.href = page;
}

// Example job structure to test logic
// applyToJob({ id: "123", company: "mycurrentcompany.com" });

