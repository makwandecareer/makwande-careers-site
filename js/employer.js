import { employerRegister } from './api.js';
const form = document.getElementById('employerForm');
const out = document.getElementById('employerOut');
form?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(form);
  const payload = Object.fromEntries(fd.entries());
  try{
    const r = await employerRegister(payload);
    out.textContent = 'Registered successfully: ' + JSON.stringify(r);
  }catch(err){
    out.textContent = 'Error (backend may not yet expose this endpoint): ' + err.message;
  }
});
