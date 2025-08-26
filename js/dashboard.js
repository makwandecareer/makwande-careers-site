import { getApplications } from './api.js';
const user = Session.get();
if(!user){ location.href = 'login.html'; }
document.getElementById('whoami').textContent = user?.email || '';
const tbody = document.getElementById('apps');
async function loadApps(){
  try{
    const apps = await getApplications(user.id);
    tbody.innerHTML = (apps||[]).map(a=>`
      <tr><td><code>${a.job_id}</code></td>
      <td><span class="badge bg-success-subtle text-success-emphasis">${a.status}</span></td>
      <td>${a.applied_at}</td><td>${a.notes ?? ''}</td></tr>`).join('');
  }catch(err){
    tbody.innerHTML = `<tr><td colspan="4" class="text-danger">Failed to load: ${err.message}</td></tr>`;
  }
}
loadApps();

