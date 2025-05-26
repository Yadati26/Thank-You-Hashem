from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import requests
import os

app = Flask(__name__)

# Load keys from Render environment variables
API_KEY = os.environ.get("COINEX_API_KEY")
SECRET_KEY = os.environ.get("COINEX_SECRET_KEY")

BASE_URL = "https://api.coinex.com/v1"

def sign_request(params, secret_key):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def send_order(market, amount, trade_type):
    url = f"{BASE_URL}/order/limit"
    tonce = str(int(time.time() * 1000))

    params = {
        "access_id": API_KEY,
        "amount": str(amount),
        "market": market.lower(),
        "price": "500000",  # Dummy price for limit order to simulate intent
        "tonce": tonce,
        "type": trade_type
    }

    signature = sign_request(params, SECRET_KEY)
    headers = {"Authorization": signature}

    response = requests.post(url, data=params, headers=headers)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON payload received"}), 400

    actions = data.get("actions")
    amount = data.get("amount")
    symbol = data.get("symbol")

    if not actions or not amount or not symbol:
        return jsonify({"error": "Missing required fields"}), 400

    results = []
    for action in actions:
        if action.lower() in ["buy", "sell"]:
            res = send_order(symbol, amount, action.lower())
            results.append(res)

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
