"""Reads opportunity rows from the Google Sheet and writes results back."""

from googleapiclient.discovery import build

from config import SHEET_ID, SHEET_TAB_NAME
from google_auth import get_google_credentials

# Column order must match the header row in your Sheet exactly, A to P
COLUMNS = [
    "Opportunity", "Link", "Type", "Organization", "Contact Name",
    "Contact Email", "Description", "Why Interested", "Experiences",
    "Questions", "Deadline", "Process", "Status", "AI Draft",
    "Gmail Status", "Slack Status",
]


def _get_service():
    creds = get_google_credentials()
    return build("sheets", "v4", credentials=creds)


def read_rows():
    """Returns a list of dicts, one per opportunity row, plus its row number
    (needed later to write results back to the correct row)."""
    service = _get_service()
    range_ = f"{SHEET_TAB_NAME}!A2:P1000"  # skip header row
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SHEET_ID, range=range_)
        .execute()
    )
    values = result.get("values", [])

    rows = []
    for i, row in enumerate(values):
        padded = row + [""] * (len(COLUMNS) - len(row))
        row_dict = dict(zip(COLUMNS, padded))
        row_dict["_row_number"] = i + 2
        rows.append(row_dict)
    return rows


def update_row(row_number, status=None, drafted_answers=None,
               gmail_status=None, slack_status=None):
    """Writes result columns back for one row."""
    service = _get_service()
    updates = []

    if status is not None:
        updates.append({
            "range": f"{SHEET_TAB_NAME}!M{row_number}",
            "values": [[status]],
        })
    if drafted_answers is not None:
        updates.append({
            "range": f"{SHEET_TAB_NAME}!N{row_number}",
            "values": [[drafted_answers]],
        })
    if gmail_status is not None:
        updates.append({
            "range": f"{SHEET_TAB_NAME}!O{row_number}",
            "values": [[gmail_status]],
        })
    if slack_status is not None:
        updates.append({
            "range": f"{SHEET_TAB_NAME}!P{row_number}",
            "values": [[slack_status]],
        })

    if updates:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"valueInputOption": "RAW", "data": updates},
        ).execute()