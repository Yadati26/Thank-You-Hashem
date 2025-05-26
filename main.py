from flask import Flask, request, jsonify
import hmac
import hashlib
import requests
import os

app = Flask(__name__)

COINEX_API_KEY = os.environ.get("COINEX_API_KEY")
COINEX_API_SECRET = os.environ.get("COINEX_API_SECRET")
COINEX_BASE_URL = "https://api.coinex.com/v1/order/limit/market"

@app.route('/')
def index():
    return 'Bot is running'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'side' not in data or 'amount' not in data or 'market' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    side = data['side'].lower()
    market = data['market']
    amount = data['amount']

    payload = {
        "access_id": COINEX_API_KEY,
        "market": market,
        "type": side,
        "amount": amount,
        "tonce": int(requests.get("https://api.coinex.com/v1/market/ticker/all").elapsed.total_seconds() * 1000)
    }

    sign = '&'.join([f"{key}={payload[key]}" for key in sorted(payload)])
    sign += f"&secret_key={COINEX_API_SECRET}"
    payload["sign"] = hashlib.md5(sign.encode()).hexdigest().upper()

    response = requests.post(COINEX_BASE_URL, data=payload)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
