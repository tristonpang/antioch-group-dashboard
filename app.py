import csv
import os

from flask import Flask, request

from constants import CSV_FILE
from dashboard import REALTIME_FLAG_FILE
from interfaces.form_response import FormResponse

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return {"message": "Welcome to the CMRA Group Dashboard API"}


@app.route("/webhook", methods=["POST"])
def webhook():
    # Check if real-time is enabled
    if not os.path.exists(REALTIME_FLAG_FILE):
        return {"status": "ignored", "reason": "real-time data not enabled"}, 200

    data = request.json
    print("Webhook received:", data["event_id"])

    # Convert into domain object FormResponse
    form_response = FormResponse(data["form_response"])

    # Flatten and write to csv file
    csv_data = form_response.parse_to_row()
    with open(CSV_FILE, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())
        writer.writerow(csv_data)

    return {"status": "success"}
