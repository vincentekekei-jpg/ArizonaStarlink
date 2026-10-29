from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# PUT YOUR REAL KEYS IN .env FILE - NOT HERE
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET", "sk_test_692ccbe5ea7e6cb30154871e797a2eb6b0ec8019")
PAYSTACK_PUBLIC = os.getenv("PAYSTACK_PUBLIC", "pk_test_10e8c42e52843921637a5addf0f608cb67d97016")

DB_FILE = "payments.log"

@app.route("/")
def home():
    return render_template("index.html", paystack_public= PAYSTACK_PUBLIC)

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    ref = data.get("reference")
    customer = data.get("customer", {})

    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    r = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    res = r.json()

    if res.get("status") and res["data"]["status"] == "success":
        amount = res["data"]["amount"] / 100
        email = res["data"]["customer"]["email"]
        
        log = f"{datetime.now()} | {email} | {customer.get('name')} | {customer.get('starlink_id')} | NGN {amount} | {ref}\n"
        with open(DB_FILE, "a") as f:
            f.write(log)
        
        print(f"✅ NEW PAYMENT: {email} - NGN {amount}")
        
        return jsonify({
            "status": "success",
            "message": f"Payment Successful! NGN {amount:,.0f} received. Arizona will activate your Starlink within 30 mins. Ref: {ref}"
        })
    else:
        return jsonify({"status": "failed", "message": "Verification failed. Contact Arizona."})

@app.route("/admin")
def admin():
    # Simple admin to see who paid
    if not os.path.exists(DB_FILE):
        return "<h2>No payments yet</h2>"
    with open(DB_FILE, "r") as f:
        logs = f.read().replace("\n", "<br>")
    return f"<body style='font-family:monospace;padding:20px'><h1>Arizona Starlink - Payments</h1><p>{logs}</p></body>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)