from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import time
import requests
import json

app = Flask(__name__)

COINEX_ACCESS_ID = os.getenv("FF25668A6AE44E409DF23EFA48D7C062")
COINEX_SECRET_KEY = os.getenv("A65A6E14A1D3C615EF169BC4896BE7206105988F3C6FA48F")

def generate_signature(params, secret_key):
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    to_sign = query_string + "&secret_key=" + secret_key
    return hmac.new(secret_key.encode(), to_sign.encode(), hashlib.sha256).hexdigest()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("Incoming webhook data:", data)

        actions = data.get("actions")
        if not actions:
            return jsonify({"error": "Missing 'actions' in payload"}), 400

        if "buy" in actions:
            side = "buy"
        elif "sell" in actions:
            side = "sell"
        else:
            return jsonify({"error": "No valid trading action in 'actions'"}), 400

        symbol = data.get("symbol", "BTCUSDT")  # Default fallback
        amount = data.get("amount", "0.001")     # Fallback amount

        print(f"Placing {side.upper()} market order for {amount} {symbol}")

        timestamp = int(time.time())
        market = symbol.replace("/", "")  # In case user uses BTC/USDT

        params = {
            "access_id": COINEX_ACCESS_ID,
            "market": market,
            "type": "market",
            "amount": amount,
            "tonce": timestamp,
        }

        if side == "buy":
            params["trade_type"] = "bid"
        else:
            params["trade_type"] = "ask"

        signature = generate_signature(params, COINEX_SECRET_KEY)
        headers = {
            "Authorization": signature,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://api.coinex.com/v1/order/put_market", data=params, headers=headers)
        print("CoinEx API response:", response.text)

        if response.status_code == 200:
            return jsonify({"status": "Order placed", "response": response.json()}), 200
        else:
            return jsonify({"error": "CoinEx API error", "response": response.text}), 500

    except Exception as e:
        print("Exception occurred:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CoinEx Trading Bot is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
