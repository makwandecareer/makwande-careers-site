import { signup, login } from './api.js';
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
loginForm?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(loginForm);
  try{
    const user = await login(fd.get('email'), fd.get('password'));
    Session.set(user);
    location.href = 'jobs.html';
  }catch(err){ alert('Login failed: ' + err.message); }
});
signupForm?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(signupForm);
  try{
    const user = await signup(fd.get('username'), fd.get('email'), fd.get('password'));
    Session.set(user);
    location.href = 'jobs.html';
  }catch(err){ alert('Signup failed: ' + err.message); }
});
