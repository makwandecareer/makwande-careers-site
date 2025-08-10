// IMPORTANT: set this to your live API URL (no trailing slash)
const API_BASE = "https://autoapply-api.onrender.com"; // <-- change to your API

// Common helper
function setMsg(id, text, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("err", !!isError);
}
function setMsgEl(el, text, isError = false) {
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("err", !!isError);
}
function escapeHtml(s = "") {
  return s.replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c]));
}

