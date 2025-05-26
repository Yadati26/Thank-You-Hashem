import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    side = data.get("side")
    symbol = data.get("symbol")
    amount = data.get("amount")
    print(f"Received alert: {side.upper()} {amount} of {symbol}")
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
