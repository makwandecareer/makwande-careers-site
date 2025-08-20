import { verifyPaystack } from './api.js';
const user = Session.get();
if(!user){ location.href = 'login.html'; }
document.getElementById('payBtn')?.addEventListener('click', ()=>{
  const amount = Number(document.getElementById('amount').value || 300);
  const currency = document.getElementById('currency').value || 'ZAR';
  if(!window.PaystackPop){ alert('Paystack SDK not loaded'); return; }
  const handler = PaystackPop.setup({
    key: pk_test_19cfb8881a1f65a03a213b94adbd1968efb7c7b3, // TODO: replace with your Paystack public key
    email: user.email,
    amount: Math.max(1, amount) * 100,
    currency,
    callback: async function(response){
      try{
        const r = await verifyPaystack(response.reference, user.id);
        alert(`Payment ${r.status}. Ref: ${r.reference}`);
        location.href = 'dashboard.html';
      }catch(err){ alert('Verify failed: ' + err.message); }
    },
    onClose: function(){ /* optional */ }
  });
  handler.openIframe();
});
