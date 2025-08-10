// jobs.js
(function () {
    const list = document.getElementById("jobList");
    const msg  = document.getElementById("jobsMsg");

    if (!list) return;

    async function loadJobs() {
        if (msg) msg.textContent = "Loading jobs…";
        try {
            const jobs = await AutoApply.fetchJobs();
            list.innerHTML = "";

            if (!Array.isArray(jobs) || jobs.length === 0) {
                list.innerHTML = "<li>No jobs found.</li>";
            } else {
                jobs.forEach(j => {
                    const li = document.createElement("li");
                    li.innerHTML = `
                        <strong>${j.title || "Untitled role"}</strong>
                        <div>${j.company || ""} — ${j.location || ""}</div>
                        <a href="${j.url || "#"}" target="_blank" rel="noopener">View</a>
                    `;
                    list.appendChild(li);
                });
            }
            if (msg) msg.textContent = "";
        } catch (err) {
            if (msg) msg.textContent = ❌ ${err.message};
        }
    }

    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            AutoApply.clearToken();
            window.location.href = "/login.html";
        });
    }

    loadJobs();
})();