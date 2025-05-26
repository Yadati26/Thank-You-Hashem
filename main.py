from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import requests
import os

app = Flask(__name__)

# Retrieve API credentials from environment variables
API_KEY = os.getenv('FF25668A6AE44E409DF23EFA48D7C062')
API_SECRET = os.getenv('A65A6E14A1D3C615EF169BC4896BE7206105988F3C6FA48F')

# CoinEx API endpoint for market orders
COINEX_API_URL = "https://api.coinex.com/v1/order/market"

def generate_signature(params, secret_key):
    """
    Generate HMAC SHA256 signature required by CoinEx API.
    """
    sorted_params = sorted(params.items())
    to_sign = '&'.join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(secret_key.encode(), to_sign.encode(), hashlib.sha256).hexdigest()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    required_fields = {'symbol', 'side', 'amount'}
    if not required_fields.issubset(data):
        return jsonify({"error": f"Missing fields: {required_fields - data.keys()}"}), 400

    symbol = data['symbol'].upper()
    side = data['side'].lower()
    amount = data['amount']

    # Prepare parameters for the CoinEx API request
    params = {
        'access_id': API_KEY,
        'market': symbol,
        'type': side,
        'amount': amount,
        'tonce': int(time.time() * 1000)
    }

    # Generate signature
    signature = generate_signature(params, API_SECRET)
    headers = {
        'Authorization': signature,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Send POST request to CoinEx API
    response = requests.post(COINEX_API_URL, data=params, headers=headers)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
