// Backend base URL (set to your Render FastAPI URL, no trailing slash)
window.API_BASE = "https://autoapplyapp.onrender.com";

// JSON helper
window.fetchJSON = async (url, opts={}) => {
  const res = await fetch(url, {headers:{'Content-Type':'application/json'}, ...opts});
  if(!res.ok){
    const t = await res.text().catch(()=>res.statusText);
    throw new Error(`${res.status} ${t}`);
  }
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
};

// Session helper
window.Session = {
  set(user){ localStorage.setItem('user', JSON.stringify(user)); },
  get(){ try{return JSON.parse(localStorage.getItem('user')||'null')}catch(_){return null} },
  clear(){ localStorage.removeItem('user'); }
};
