import csv
import os

from flask import Flask, request

from constants import CSV_FILE
from interfaces.form_response import FormResponse

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return {"message": "Welcome to the CMRA Group Dashboard API"}


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook received:", data["event_id"])

    # Convert into domain object FormResponse
    form_response = FormResponse(data["form_response"])

    # Check if CSV file exists and has headers
    is_file_exists = os.path.exists(CSV_FILE)
    is_empty_file = not is_file_exists or os.path.getsize(CSV_FILE) == 0

    # Flatten and write to csv file
    csv_data = form_response.parse_to_row()
    with open(CSV_FILE, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())

        if is_empty_file:
            writer.writeheader()

        writer.writerow(csv_data)

    return {"status": "success"}


def clear_csv():
    """Clear the CSV file."""
    with open("form_responses.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[])
        writer.writeheader()
