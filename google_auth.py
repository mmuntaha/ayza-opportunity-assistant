"""Handles the one-time Google login flow (OAuth) shared by Sheets and Gmail.

First run: opens a browser window asking you to approve access.
Every run after that: reuses the saved token.json, no login needed.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import GOOGLE_SCOPES

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_google_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} not found. Download it from Google "
                    f"Cloud Console (see README step 2) and place it in this "
                    f"folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds
