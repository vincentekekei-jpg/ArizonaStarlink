async function payNow(){
  const fullName = document.getElementById('fullName')?.value || document.querySelector('input[name="fullName"]')?.value || document.getElementById('name')?.value || "Customer";
  const email = document.getElementById('email')?.value;
  const phone = document.getElementById('phone')?.value || document.getElementById('kitId')?.value || "08000000000";
  const planSelect = document.getElementById('plan');
  const amount = planSelect.value;
  const plan_name = planSelect.options[planSelect.selectedIndex].dataset.name;

  if(!email){ alert("Please enter email"); return; }

  const btn = document.getElementById('payBtn');
  const originalText = btn.innerHTML;
  btn.innerHTML = "Processing...";
  btn.disabled = true;

  try{
    const res = await fetch('/initialize', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email, amount, plan_name, full_name: fullName, phone})
    });
    const data = await res.json();
    
    if(!data.status){
      alert('Error: ' + (data.message || 'Failed to initialize'));
      btn.innerHTML = originalText;
      btn.disabled = false;
      return;
    }

    const handler = PaystackPop.setup({
      key: PAYSTACK_PUBLIC_KEY,
      email: email,
      amount: data.data.amount,
      ref: data.data.reference,
      metadata: {full_name: fullName, plan_name, phone},
      callback: function(response){
        // AUTO REDIRECT TO PIN PAGE!
        window.location.href = '/verify/' + response.reference;
      },
      onClose: function(){
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    });
    handler.openIframe();
  }catch(err){
    alert("Network error: " + err.message);
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}