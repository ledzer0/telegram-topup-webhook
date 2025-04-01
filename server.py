from flask import Flask, request
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests

app = Flask(__name__)
CREDITS_FILE = "credits.json"

# Google Sheets setup
def get_sheet():
    creds = json.loads(os.getenv("GOOGLE_SERVICE_JSON"))
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("Logs")

def log_event(event, user_id, amount, notes="Webhook Auto Topup"):
    try:
        sheet = get_sheet()
        sheet.append_row([
            datetime.now().isoformat(),
            event,
            str(user_id),
            "-",
            str(amount),
            notes
        ])
    except Exception as e:
        print(f"Sheet log failed: {e}")

def load_json(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

@app.route("/toyyibpay", methods=["POST"])
def toyyibpay_webhook():
    data = request.form
    if data.get("billpaymentStatus") == "1":
        telegram_id = data.get("billExternalReferenceNo")
        if telegram_id:
            credits = load_json(CREDITS_FILE)
            credits.setdefault(telegram_id, {"credits": 5})
            credits[telegram_id]["credits"] += 10
            save_json(CREDITS_FILE, credits)

            # Log and notify
            log_event("Auto Topup", telegram_id, 10)
            try:
                BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    data={"chat_id": telegram_id, "text": "✅ Payment received! 10 message credits added."}
                )
            except: pass
            return "OK", 200
    return "Ignored", 200

@app.route("/", methods=["GET"])
def home():
    return "ToyyibPay Webhook is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)