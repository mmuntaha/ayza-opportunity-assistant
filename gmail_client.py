"""Creates Gmail DRAFTS (never sends automatically) for outreach opportunities."""

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from google_auth import get_google_credentials


def _get_service():
    creds = get_google_credentials()
    return build("gmail", "v1", credentials=creds)


def create_draft(to_email: str, subject: str, body: str) -> str:
    """Creates a Gmail draft and returns its draft ID (useful for logging /
    verifying in reliability tests)."""
    if not to_email:
        raise ValueError("Cannot create a draft with no recipient email.")

    service = _get_service()

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw_message}})
        .execute()
    )
    return draft["id"]
