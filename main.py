from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Thank You, Hashem bot is live."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received raw payload:", data)

    side = data.get("side", "").upper()
    amount = data.get("amount", "N/A")
    symbol = data.get("symbol", "N/A")

    print(f"Received alert: {side} {amount} of {symbol}")
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
