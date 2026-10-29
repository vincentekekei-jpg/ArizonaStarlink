import os
import json
import random
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Read keys from Render Environment (secure)
PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET", "sk_test_692ccbe5ea7e6cb30154871e797a2eb6b0ec8019")
PAYSTACK_PUBLIC = os.environ.get("PAYSTACK_PUBLIC", "pk_test_10e8c42e52843921637a5addf0f608cb67d97016")

# Plans duration
PLAN_DAYS = {
    "1 Month": 30,
    "2 Months": 60,
    "3 Months": 90,
    "6 Months": 180,
    "12 Months": 365,
    "1 Week": 7,
    "4 Months": 120
}

def generate_pin():
    numbers = ''.join(random.choices(string.digits, k=4))
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"AZ-{numbers}-{letters}"

@app.route('/')
def index():
    return render_template('index.html', paystack_public=PAYSTACK_PUBLIC)

@app.route('/initialize', methods=['POST'])
def initialize():
    data = request.get_json()
    email = data.get('email')
    amount = data.get('amount')  # in naira, we convert to kobo
    plan_name = data.get('plan_name')
    full_name = data.get('full_name')
    
    # Paystack expects kobo
    amount_kobo = int(float(amount) * 100)
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": amount_kobo,
        "metadata": {
            "full_name": full_name,
            "plan_name": plan_name,
            "custom_fields": [
                {"display_name": "Plan", "variable_name": "plan", "value": plan_name}
            ]
        }
    }
    r = requests.post("https://api.paystack.co/transaction/initialize", json=payload, headers=headers)
    return jsonify(r.json())

@app.route('/verify/<reference>')
def verify(reference):
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    r = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    data = r.json()
    
    if data['status'] and data['data']['status'] == 'success':
        # Payment success -> Generate PIN
        metadata = data['data'].get('metadata', {})
        plan_name = metadata.get('plan_name', '1 Month')
        email = data['data']['customer']['email']
        amount = data['data']['amount'] / 100
        full_name = metadata.get('full_name', 'Customer')
        
        pin = generate_pin()
        days = PLAN_DAYS.get(plan_name, 30)
        expiry = datetime.now() + timedelta(days=days)
        
        record = {
            "pin": pin,
            "email": email,
            "full_name": full_name,
            "plan": plan_name,
            "amount": amount,
            "days": days,
            "expiry": expiry.strftime("%Y-%m-%d"),
            "date": datetime.now().isoformat(),
            "reference": reference,
            "shared_users": 1,
            "status": "active"
        }
        
        # Save to file (will be on Render disk - for now)
        try:
            with open("vouchers.json", "a") as f:
                f.write(json.dumps(record) + "\n")
        except:
            pass
        
        return render_template('success.html', pin=pin, plan=plan_name, days=days, expiry=expiry.strftime("%Y-%m-%d"), email=email, full_name=full_name, amount=amount)
    else:
        return render_template('failed.html')

@app.route('/admin/vouchers')
def list_vouchers():
    vouchers = []
    try:
        with open("vouchers.json", "r") as f:
            for line in f:
                vouchers.append(json.loads(line))
    except FileNotFoundError:
        pass
    # Show newest first
    vouchers.reverse()
    return render_template('vouchers.html', vouchers=vouchers)

if __name__ == '__main__':
    app.run(debug=True)