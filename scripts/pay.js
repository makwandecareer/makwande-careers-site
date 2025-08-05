// pay.js
const PAYSTACK_PUBLIC_KEY = 'pk_test_xxxxxxxxxxxxxxxx';  // Replace with your real public key
const BACKEND_URL = 'https://autoapply-api.onrender.com/api/jobs';

function payWithPaystack() {
    const email = document.getElementById('email').value;
    const handler = PaystackPop.setup({
        key: PAYSTACK_PUBLIC_KEY,
        email: email,
        amount: 30000, // R300 = 30000 kobo
        currency: "ZAR",
        callback: function (response) {
            fetch(`${BACKEND_URL}/api/verify_payment/${response.reference}`)
                .then(res => res.json())
                .then(data => {
                    alert("Payment successful and verified!");
                    window.location.href = "dashboard.html";
                })
                .catch(() => {
                    alert("Payment verification failed.");
                });
        },
        onClose: function () {
            alert('Transaction was not completed.');
        }
    });
    handler.openIframe();
}

document.getElementById("pay-button").addEventListener("click", payWithPaystack);
