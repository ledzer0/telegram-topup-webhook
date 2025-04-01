from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

CREDITS_FILE = "credits.json"
API_KEY = "l0f6cyv6-tv47-hdlz-xqas-to1o6j1amh6v"

# Load credits from file
def load_credits():
    try:
        with open(CREDITS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Save credits to file
def save_credits(data):
    with open(CREDITS_FILE, "w") as f:
        json.dump(data, f)

@app.route("/", methods=["GET"])
def index():
    return "ToyyibPay Auto Topup Webhook is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.form.to_dict()
    
    print("Webhook received:", data)

    # Make sure payment is successful
    if data.get("paymentStatus") == "1":  # "1" = successful
        ref = data.get("billExternalReferenceNo", "")
        if ref.isdigit():
            user_id = ref
            credits = load_credits()
            credits.setdefault(user_id, {"credits": 5})  # default if not in file
            credits[user_id]["credits"] += 10  # top up 10 messages
            save_credits(credits)
            print(f"Auto-topped up 10 messages for user {user_id}")
            return jsonify({"status": "success"}), 200

    return jsonify({"status": "ignored"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
