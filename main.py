"""Runs the full pipeline: read Sheet -> draft via Claude -> write to
Gmail/Sheet -> remind via Slack. Designed to keep going even if one row
fails, and to report clearly what happened to each row."""

from datetime import datetime, date

import config
import sheets_client
import gmail_client
import slack_client
import agent


def days_until(deadline_str: str):
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        return (deadline - date.today()).days
    except (ValueError, TypeError):
        return None


def process_row(row: dict) -> str:
    """Handles one row. Returns a short status string for the summary log."""
    row_number = row["_row_number"]

    if row.get("Status", "").strip().lower() == "completed":
        return f"Row {row_number}: skipped (already marked Completed)"

    row_type = row.get("Type", "").strip().lower()

    try:
        if row_type == "outreach":
            drafted = agent.draft_outreach_email(row)
            gmail_client.create_draft(
                to_email=row.get("Contact Email", ""),
                subject=drafted["subject"],
                body=drafted["body"],
            )
            sheets_client.update_row(
                row_number, status="Completed", gmail_status="Draft Created"
            )
            result = f"Row {row_number}: outreach email drafted in Gmail ✅"

        elif row_type == "application":
            answers = agent.draft_application_answers(row)
            sheets_client.update_row(
                row_number, status="Completed", drafted_answers=answers
            )
            result = f"Row {row_number}: application answers written to Sheet ✅"

        else:
            result = (
                f"Row {row_number}: skipped (Type must be 'outreach' or "
                f"'application', got '{row.get('Type')}')"
            )
            print(f"[warning] {result}")
            return result

    except ValueError as e:
        result = f"Row {row_number}: skipped — {e}"
        print(f"[warning] {result}")
        return result

    except Exception as e:
        result = f"Row {row_number}: FAILED unexpectedly — {e}"
        print(f"[error] {result}")
        sheets_client.update_row(row_number, status="Failed")
        return result

    deadline_str = row.get("Deadline", "").strip()
    if deadline_str:
        days_left = days_until(deadline_str)
        if days_left is not None and 0 <= days_left <= 14:
            sent = slack_client.send_reminder(
                f":alarm_clock: Reminder: *{row.get('Link')}* is due in "
                f"{days_left} day(s) (deadline {deadline_str})."
            )
            sheets_client.update_row(
                row_number,
                slack_status="Sent" if sent else "Not Sent",
            )
            if not sent:
                result += " (Slack reminder failed — see log above)"

    return result


def main():
    print("Checking configuration...")
    config.check_config()

    print("Reading opportunities from Google Sheet...")
    rows = sheets_client.read_rows()
    print(f"Found {len(rows)} row(s).\n")

    if not rows:
        print("No rows to process. Add opportunities to your Sheet and re-run.")
        return

    summary = []
    for row in rows:
        summary.append(process_row(row))

    print("\n--- Run summary ---")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()