import csv

from flask import Flask, request

from interfaces.form_response import FormResponse

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook received:", data["event_id"])

    # Convert into domain object FormResponse
    form_response = FormResponse(data["form_response"])

    # Flatten and write to csv file
    csv_data = form_response.parse_to_row()
    with open("form_responses.csv", "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())
        writer.writerow(csv_data)

    return {"status": "success"}


def clear_csv():
    """Clear the CSV file."""
    with open("form_responses.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[])
        writer.writeheader()
