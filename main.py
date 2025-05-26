from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Load keys from environment variables
API_KEY = os.environ.get("COINEX_API_KEY")
SECRET_KEY = os.environ.get("COINEX_SECRET_KEY")

BASE_URL = "https://api.coinex.com/v1/order/limit"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "No JSON received", 400

    actions = data.get("actions", [])
    amount = data.get("amount")
    symbol = data.get("symbol")

    print(f"Received data: {data}")

    for action in actions:
        side = "buy" if action == "buy" else "sell"
        payload = {
            "market": symbol,
            "type": side,
            "amount": amount,
            "price": "99999999" if side == "buy" else "0.00000001"
        }

        headers = {
            "Content-Type": "application/json",
            "X-CoinEx-Key": API_KEY,
            "X-CoinEx-Signature": SECRET_KEY
        }

        response = requests.post(BASE_URL, json=payload, headers=headers)
        print(f"CoinEx API response: {response.text}")

    return "Order processed", 200

@app.route("/", methods=["GET"])
def home():
    return "CoinEx Trading Bot is running.", 200
