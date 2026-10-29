const planSelect = document.getElementById("plan");
const payBtn = document.getElementById("payBtn");

planSelect.addEventListener("change", () => {
  payBtn.innerText = `Pay ₦${Number(planSelect.value).toLocaleString()} with Paystack`;
});
payBtn.innerText = `Pay ₦${Number(planSelect.value).toLocaleString()} with Paystack`;

function payNow() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const kit = document.getElementById("kit").value.trim();
  const amount = document.getElementById("plan").value;
  const planName = planSelect.options[planSelect.selectedIndex].dataset.name;

  if (!name || !email) {
    alert("Please enter your full name and email");
    return;
  }

  payBtn.innerText = "Processing...";
  payBtn.disabled = true;

  let handler = PaystackPop.setup({
    key: PAYSTACK_PUBLIC_KEY,
    email: email,
    amount: amount * 100,
    currency: "NGN",
    ref: "ARZ-" + Math.floor(Math.random() * 1000000000),
    metadata: {
      custom_fields: [
        { display_name: "Full Name", variable_name: "full_name", value: name },
        { display_name: "Kit ID", variable_name: "kit_id", value: kit },
        { display_name: "Plan", variable_name: "plan", value: planName }
      ]
    },
    callback: function(response) {
      fetch("/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reference: response.reference,
          customer: { name, email, starlink_id: kit, plan: planName }
        })
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        payBtn.innerText = `Pay ₦${Number(amount).toLocaleString()} with Paystack`;
        payBtn.disabled = false;
        if (data.status === "success") {
          document.getElementById("name").value = "";
          document.getElementById("email").value = "";
        }
      });
    },
    onClose: function() {
      payBtn.innerText = `Pay ₦${Number(amount).toLocaleString()} with Paystack`;
      payBtn.disabled = false;
    }
  });
  handler.openIframe();
}