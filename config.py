"""Loads settings from .env so nothing is hardcoded in the code."""

import os
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("SHEET_ID")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Google OAuth scopes: read/write Sheets, and create Gmail drafts (not send)
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.compose",
]

SHEET_TAB_NAME = "Opportunities"
ABOUT_ME_FILE = "about_me.txt"


def check_config():
    """Fail loudly and early if something required is missing, instead of
    crashing halfway through a run with a confusing error."""
    missing = []
    if not SHEET_ID:
        missing.append("SHEET_ID")
    if not SLACK_BOT_TOKEN:
        missing.append("SLACK_BOT_TOKEN")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required .env values: {', '.join(missing)}. "
            f"Copy .env.example to .env and fill these in."
        )