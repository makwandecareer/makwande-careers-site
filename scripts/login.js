// login.js
(function () {
    const form = document.getElementById("loginForm");
    const msg  = document.getElementById("loginMsg");

    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (msg) msg.textContent = "Logging in…";

        const payload = {
            email: form.email.value.trim(),
            password: form.password.value
        };

        try {
            await AutoApply.login(payload);
            if (msg) msg.textContent = "✅ Logged in!";
            window.location.href = "/jobs.html";
        } catch (err) {
            if (msg) msg.textContent = ❌ ${err.message};
        }
    });
})();