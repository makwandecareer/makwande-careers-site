import { recruiterPost } from './api.js';
const form = document.getElementById('recruiterForm');
const out = document.getElementById('recruiterOut');
form?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(form);
  const payload = Object.fromEntries(fd.entries());
  try{
    const r = await recruiterPost(payload);
    out.textContent = 'Posted successfully: ' + JSON.stringify(r);
  }catch(err){
    out.textContent = 'Error (backend may not yet expose this endpoint): ' + err.message;
  }
});
