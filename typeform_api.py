import csv
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from constants import COMPARISON_CSV_FILE, CSV_FILE
from interfaces.form_response import CSV_HEADERS, FormResponse

load_dotenv()

TYPEFORM_API_TOKEN = os.getenv("TYPEFORM_API_TOKEN")
FORM_ID = os.getenv("TYPEFORM_FORM_ID")


def fetch_typeform_responses(start_datetime, end_datetime, is_comparison=False):
    """
    Fetch responses from Typeform API between start_datetime and end_datetime,
    and overwrite the form_responses.csv file.
    """
    url = f"https://api.typeform.com/forms/{FORM_ID}/responses"
    headers = {"Authorization": f"Bearer {TYPEFORM_API_TOKEN}"}
    params = {
        "response_type": "completed",
        "page_size": 1000,
        "since": start_datetime.isoformat() + "Z" if start_datetime else None,
        "until": end_datetime.isoformat() + "Z" if end_datetime else None,
    }

    all_responses = []
    next_token = None

    while True:
        if next_token:
            params["after"] = next_token
        print("Fetching page with url:", url)
        print("Params:", params)
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        all_responses.extend(items)
        next_token = data.get("page", {}).get("after")
        if not next_token or not items:
            break

    # Parse responses into a DataFrame
    rows = []
    for item in all_responses:
        form_response = FormResponse(item)
        row = form_response.parse_to_row()

        # answers = {
        #     a["field"]["ref"]: a.get("text")
        #     or a.get("email")
        #     or a.get("number")
        #     or a.get("date")
        #     for a in item.get("answers", [])
        # }
        # record = {"submitted_at": item.get("submitted_at"), **answers}
        rows.append(row)

    df = pd.DataFrame(rows)
    csv_file_path = COMPARISON_CSV_FILE if is_comparison else CSV_FILE
    df.to_csv(csv_file_path, index=False)
    print(f"Saved {len(df)} responses to {csv_file_path}")


def clear_csv():
    """Clear the CSV file."""
    with open("form_responses.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        writer.writeheader()
    with open("comparison_form_responses.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        writer.writeheader()


# Example usage:
# fetch_typeform_responses(
#     datetime(2025, 4, 1, 0, 0, 0),
#     datetime(2025, 7, 31, 23, 59, 59)
# )

if __name__ == "__main__":
    fetch_typeform_responses(
        # datetime(2025, 4, 1, 0, 0, 0),
        None,
        datetime(2025, 7, 31, 23, 59, 59),
    )
