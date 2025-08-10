// ⚠️ Set this to your live API base URL (absolute, no trailing slash)
const API_BASE = "https://autoapply-api.onrender.com"; // <-- change to YOUR API URL

// Endpoints used below (change only if your backend differs)
const ENDPOINTS = {
  signup: ${API_BASE}/auth/signup,
  login: ${API_BASE}/auth/login,
  me: ${API_BASE}/auth/me,
  jobs: ${API_BASE}/api/jobs,
};

export { API_BASE, ENDPOINTS };

