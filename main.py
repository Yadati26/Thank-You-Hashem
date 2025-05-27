from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import requests
import os

app = Flask(__name__)

# Corrected environment variable names
ACCESS_ID = os.environ.get("COINEX_ACCESS_ID")
SECRET_KEY = os.environ.get("COINEX_SECRET_KEY")

BASE_URL = "https://api.coinex.com/v1"

def sign(params):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    to_sign = query_string + f"&secret_key={SECRET_KEY}"
    return hashlib.md5(to_sign.encode()).hexdigest().upper()

def place_order(market, side, amount):
    url = f"{BASE_URL}/order/market"
    params = {
        "access_id": ACCESS_ID,
        "market": market,
        "type": side,
        "amount": amount,
        "tonce": int(time.time() * 1000),
    }
    params["sign"] = sign(params)
    response = requests.post(url, data=params)
    return response.json()

@app.route("/", methods=["GET"])
def home():
    return "Bot is live."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    actions = data.get("actions", [])
    market = "BTCUSDT"
    amount = "0.001"

    results = []

    if "close" in actions:
        res = place_order(market, "sell", amount)
        results.append({"action": "close", "response": res})

    if "buy" in actions:
        res = place_order(market, "buy", amount)
        results.append({"action": "buy", "response": res})

    return jsonify({"status": "success", "results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
