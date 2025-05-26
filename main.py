from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    symbol = data.get('symbol')
    side = data.get('side')
    amount = data.get('amount')
    api_key = data.get('api_key')
    secret_key = data.get('secret_key')

    print(f"Received alert: {side.upper()} {amount} of {symbol}")
    print(f"API Key: {api_key}")
    print(f"Secret Key: {secret_key}")

    # Placeholder: you will replace this with real CoinEx trading logic
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
