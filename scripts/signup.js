// signup.js
(function () {
    const form = document.getElementById("signupForm");
    const msg  = document.getElementById("signupMsg");

    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (msg) msg.textContent = "Creating your account…";

        const payload = {
            email: form.email.value.trim(),
            password: form.password.value,
            full_name: form.full_name ? form.full_name.value.trim() : undefined
        };

        try {
            await AutoApply.signup(payload);
            if (msg) msg.textContent = "✅ Signup successful! You can now log in.";
            form.reset();
        } catch (err) {
            if (msg) msg.textContent = ❌ ${err.message};
        }
    });
})();