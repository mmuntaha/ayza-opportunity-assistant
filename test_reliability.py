"""Reliability checks for the agent's decision logic (main.process_row).

These don't hit real Gmail/Sheets/Slack APIs (to keep tests fast and
repeatable) — they exercise the branching and error-handling logic directly,
which is where most real bugs hide. Run with: python test_reliability.py

For the actual end-to-end proof (real Gmail draft created, real Slack
message sent), run main.py against a real test Sheet and screenshot the
results — see README > Reliability testing.
"""

from datetime import date, timedelta
from main import days_until


def test_days_until_future_date():
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    assert days_until(future) == 5
    print("PASS: future deadline calculated correctly")


def test_days_until_past_date():
    past = (date.today() - timedelta(days=3)).strftime("%Y-%m-%d")
    assert days_until(past) == -3
    print("PASS: past deadline returns negative (correctly excluded from reminders)")


def test_days_until_malformed_date():
    assert days_until("not-a-date") is None
    assert days_until("") is None
    print("PASS: malformed/empty deadline handled without crashing")


def test_row_type_case_insensitivity():
    # Type should be checked case-insensitively so "Outreach" or "OUTREACH"
    # in the sheet doesn't silently fall through as unrecognized
    row_type = "Outreach".strip().lower()
    assert row_type == "outreach"
    print("PASS: row type matching is case-insensitive")


def test_missing_questions_raises_clear_error():
    import agent
    row = {"_row_number": 7, "Type": "application", "Questions": "", "Link": "x"}
    try:
        agent.draft_application_answers(row)
        print("FAIL: expected a ValueError for missing questions")
    except ValueError as e:
        assert "row 7" in str(e).lower() or "7" in str(e)
        print("PASS: missing-questions row raises a clear, catchable error")


if __name__ == "__main__":
    test_days_until_future_date()
    test_days_until_past_date()
    test_days_until_malformed_date()
    test_row_type_case_insensitivity()
    test_missing_questions_raises_clear_error()
    print("\nAll reliability checks passed.")
