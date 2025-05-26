from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import time
import json

app = Flask(__name__)

COINEX_BASE_URL = "https://api.coinex.com/v1"

def coinex_request(api_key, secret_key, endpoint, method="POST", params=None):
    if params is None:
        params = {}

    timestamp = int(time.time())
    params.update({
        "access_id": api_key,
        "tonce": timestamp
    })

    sorted_params = sorted(params.items())
    query_str = '&'.join(f"{k}={v}" for k, v in sorted_params)
    signature = hmac.new(
        secret_key.encode(),
        query_str.encode(),
        hashlib.sha256
    ).hexdigest().upper()

    headers = {
        "Authorization": signature
    }

    url = f"{COINEX_BASE_URL}{endpoint}"

    if method.upper() == "POST":
        response = requests.post(url, headers=headers, data=params)
    else:
        response = requests.get(url, headers=headers, params=params)

    return response.json()

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        symbol = data.get("symbol", "BTCUSDT")
        side = data.get("side", "buy").lower()
        amount = float(data.get("amount", 0))
        api_key = data["api_key"]
        secret_key = data["secret_key"]

        if not api_key or not secret_key:
            return jsonify({"error": "Missing API credentials"}), 400

        market = symbol.lower()
        endpoint = "/order/limit"

        if side == "buy":
            price_resp = requests.get(f"{COINEX_BASE_URL}/market/ticker?market={market}")
            price = float(price_resp.json()["data"]["ticker"]["buy"])
        elif side == "sell":
            price_resp = requests.get(f"{COINEX_BASE_URL}/market/ticker?market={market}")
            price = float(price_resp.json()["data"]["ticker"]["sell"])
        else:
            return jsonify({"error": "Invalid side"}), 400

        order_data = {
            "market": market,
            "type": side,
            "amount": amount,
            "price": round(price, 2)
        }

        res = coinex_request(api_key, secret_key, endpoint, "POST", order_data)
        return jsonify(res)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
