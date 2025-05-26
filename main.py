from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import time
import requests

app = Flask(__name__)

# Fetch CoinEx API credentials from environment
COINEX_API_KEY = os.environ.get("COINEX_API_KEY")
COINEX_SECRET_KEY = os.environ.get("COINEX_SECRET_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received data:", data)

    actions = data.get("actions", [])
    amount = data.get("amount")
    symbol = data.get("symbol")

    if not COINEX_API_KEY or not COINEX_SECRET_KEY:
        return jsonify({"error": "CoinEx credentials not set"}), 500

    if "buy" in actions:
        response = place_order("buy", symbol, amount)
        print("CoinEx API response:", response.text)

    if "sell" in actions or "close" in actions:
        response = place_order("sell", symbol, amount)
        print("CoinEx API response:", response.text)

    return "", 200

def place_order(side, market, amount):
    url = "https://api.coinex.com/v1/order/limit"

    tonce = str(int(time.time() * 1000))

    params = {
        "access_id": COINEX_API_KEY,
        "market": market,
        "type": side,
        "amount": str(amount),
        "price": "50000",  # Placeholder price, real-time pricing needs a fetch first
        "tonce": tonce
    }

    sorted_params = sorted(params.items())
    query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
    to_sign = query_string + f"&secret_key={COINEX_SECRET_KEY}"

    signature = hashlib.md5(to_sign.encode()).hexdigest().upper()
    headers = {
        "Content-Type": "application/json",
        "Authorization": signature
    }

    return requests.post(url, json=params, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
