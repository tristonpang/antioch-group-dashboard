import csv
import gc
import json
import os

import streamlit as st
from tornado.routing import PathMatches, Rule
from tornado.web import Application, RequestHandler

from constants import CSV_FILE, REALTIME_FLAG_FILE
from interfaces.form_response import FormResponse


@st.cache_resource()
def setup_api_handler(uri, handler):
    print("Setup Tornado. Should be called only once")

    # Get instance of Tornado
    tornado_app = next(
        o for o in gc.get_referrers(Application) if o.__class__ is Application
    )

    # Setup custom handler
    tornado_app.wildcard_router.rules.insert(0, Rule(PathMatches(uri), handler))


# === Usage ======
class EmbeddedApiHandler(RequestHandler):
    def check_xsrf_cookie(self):
        # This handler will not perform XSRF checks
        pass

    def get(self):
        self.write({"message": "Welcome to the CMRA Group Dashboard API"})

    def post(self):
        # Check if real-time is enabled
        if not os.path.exists(REALTIME_FLAG_FILE):
            self.write({"status": "ignored", "reason": "real-time data not enabled"})
            return

        # Get raw bytes
        raw_body = self.request.body

        # Decode to string (if needed)
        body_str = raw_body.decode("utf-8")

        data = json.loads(body_str)
        print("Webhook received:", data["event_id"])

        # Convert into domain object FormResponse
        form_response = FormResponse(data["form_response"])

        # Flatten and write to csv file
        csv_data = form_response.parse_to_row()
        with open(CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())
            writer.writerow(csv_data)

        self.write({"status": "success"})
