import os
import time
import hmac
import hashlib
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ENV variables from Render
ACCESS_ID = os.getenv("COINEX_ACCESS_ID")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

# CoinEx API endpoint
BASE_URL = "https://api.coinex.com/v1/order/market"

def generate_signature(params, secret_key):
    param_str = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    sign_str = param_str + f"&secret_key={secret_key}"
    return hmac.new(secret_key.encode(), sign_str.encode(), hashlib.sha256).hexdigest().upper()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received data:", data)

    try:
        action = data["actions"][0].lower()  # "buy" or "sell"
        symbol = data["symbol"]              # e.g. "BTCUSDT"
        amount = float(data["amount"])       # e.g. 0.0005
    except Exception as e:
        return f"Invalid payload format: {str(e)}", 400

    # CoinEx needs symbol with dash: BTC-USDT instead of BTCUSDT
    if "-" not in symbol:
        symbol = symbol[:3] + "-" + symbol[3:]

    market = symbol.upper()
    timestamp = int(time.time())

    params = {
        "access_id": ACCESS_ID,
        "amount": str(amount),
        "market": market,
        "type": action,
        "tonce": timestamp,
    }

    signature = generate_signature(params, SECRET_KEY)
    headers = {
        "Authorization": signature,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(BASE_URL, data=params, headers=headers)
        print("CoinEx API response:", response.text)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print("Request to CoinEx failed:", e)
        return f"Request failed: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=False, port=10000)
