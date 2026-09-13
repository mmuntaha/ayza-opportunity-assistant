"""Sends deadline reminder messages to Slack."""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import SLACK_BOT_TOKEN, SLACK_CHANNEL

_client = WebClient(token=SLACK_BOT_TOKEN)


def send_reminder(text: str) -> bool:
    """Sends a message to Slack. Returns True/False instead of crashing the
    whole pipeline if Slack is down or misconfigured — Sheets/Gmail work
    should still complete even if Slack fails."""
    try:
        _client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
        return True
    except SlackApiError as e:
        print(f"[Slack error] Could not send reminder: {e.response['error']}")
        return False
