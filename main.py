from pathlib import Path

code = '''
import os
import hmac
import hashlib
import time
import json
from flask import Flask, request
import requests

app = Flask(__name__)

COINEX_API_KEY = os.getenv("COINEX_API_KEY")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

def coinex_v2_request(method, path, payload=None):
    url = f"https://api.coinex.com/v2/{path}"
    timestamp = str(int(time.time() * 1000))
    payload_str = json.dumps(payload) if payload else ""
    signature_base = f"{timestamp}{path}{payload_str}".encode()
    signature = hmac.new(COINEX_SECRET_KEY.encode(), signature_base, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-CoinEx-Key": COINEX_API_KEY,
        "X-CoinEx-Sign": signature,
        "X-CoinEx-Timestamp": timestamp
    }

    response = requests.request(method, url, headers=headers, data=payload_str)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"Received data: {data}")

    actions = data.get("actions", [])
    symbol = data.get("symbol", "")
    amount = data.get("amount", 0)

    for action in actions:
        if action.lower() == "buy":
            payload = {
                "market": symbol,
                "amount": str(amount),
                "price": "0",  # Market order
                "type": "market",
                "side": "buy"
            }
            res = coinex_v2_request("POST", "spot/order", payload)
            print("Buy response:", res)

        elif action.lower() == "close":
            payload = {
                "market": symbol,
                "amount": str(amount),
                "price": "0",  # Market order
                "type": "market",
                "side": "sell"
            }
            res = coinex_v2_request("POST", "spot/order", payload)
            print("Sell response:", res)

    return "ok", 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
'''

path = Path("/mnt/data/main.py")
path.write_text(code)
path
