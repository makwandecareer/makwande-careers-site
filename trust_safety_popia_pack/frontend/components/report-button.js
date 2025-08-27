// report-button.js
// Usage: include this script and add data-job-id on each job card's "Report" button.

(function(){
  async function reportJob(jobId, reason, details){
    const res = await window.apiFetch('/api/trust/report', {
      method: 'POST',
      body: { job_id: jobId, reason, details }
    });
    return res;
  }

  function openDialog(jobId){
    const reason = prompt('Why is this job suspicious? (e.g., pay-to-apply, crypto scheme)');
    if (!reason) return;
    const details = prompt('Any details? (optional)') || '';
    reportJob(jobId, reason, details)
      .then(r => alert('Thanks! Ticket: ' + r.ticket_id))
      .catch(e => alert('Error: ' + e.message));
  }

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-report-job]');
    if (!btn) return;
    const jobId = btn.getAttribute('data-job-id');
    if (jobId) openDialog(jobId);
  });
})();
