from datetime import timedelta, timezone

CSV_FILE = "form_responses.csv"
COMPARISON_CSV_FILE = "comparison_form_responses.csv"
REALTIME_FLAG_FILE = "realtime_enabled.flag"

ALL_ROLES_OPTION = "All"
EMPTY_ROLE_OPTION = "Empty/Unknown"

UTC_PLUS_8 = timezone(timedelta(hours=8))
