from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    side = data.get("side", "").upper()
    symbol = data.get("symbol", "UNKNOWN")
    amount = data.get("amount", 0)

    print(f"Received alert: {side} {amount} of {symbol}")

    # Placeholder for sending to CoinEx
    return jsonify({"status": "received"}), 200

@app.route('/', methods=['GET'])
def health_check():
    return "OK", 200
