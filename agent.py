"""The reasoning core. Given one opportunity row, decides what to write and
writes it — a personalized outreach email, or tailored answers to specific
application questions — grounded in the user's own background info."""

import google.generativeai as genai

from config import GEMINI_API_KEY, ABOUT_ME_FILE

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-3.6-flash")


def _load_about_me() -> str:
    try:
        with open(ABOUT_ME_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "No background info provided."


def draft_outreach_email(row: dict) -> dict:
    """Returns {"subject": ..., "body": ...} for an outreach-type row."""
    about_me = _load_about_me()

    prompt = f"""You are helping someone write a short, genuine outreach email
about an opportunity they found. Do not sound like a form letter.

About the sender:
{about_me}

Opportunity details:
- Link: {row.get('Link')}
- Contact name: {row.get('Contact Name')}

Write a concise, warm, professional email (under 150 words) introducing the
sender and expressing genuine interest in this opportunity, referencing
relevant background naturally. End with a clear, low-pressure ask (e.g. a
short call, or how to proceed).

Respond in exactly this format, nothing else:
SUBJECT: <subject line>
BODY:
<email body>"""

    response = _model.generate_content(prompt)
    text = response.text

    subject = "Following up on an opportunity"
    body = text
    if "SUBJECT:" in text and "BODY:" in text:
        subject = text.split("SUBJECT:")[1].split("BODY:")[0].strip()
        body = text.split("BODY:")[1].strip()

    return {"subject": subject, "body": body}


def draft_application_answers(row: dict) -> str:
    """Returns a formatted string of Q&A pairs for an application-type row."""
    about_me = _load_about_me()
    raw_questions = row.get("Questions", "")

    if not raw_questions.strip():
        raise ValueError(
            f"Row {row.get('_row_number')} is type 'application' but has no "
            f"Questions listed — skipping to avoid generating a useless answer."
        )

    questions = [q.strip() for q in raw_questions.split("|") if q.strip()]

    prompt = f"""You are helping someone answer specific application
questions for an opportunity, using only their real background below.
Do not invent facts not implied by their background. Keep each answer
genuine, specific, and under 100 words.

About the applicant:
{about_me}

Opportunity link: {row.get('Link')}

Answer each of these questions separately, clearly labeled:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

Respond in exactly this format for each question:
Q: <question>
A: <answer>
"""

    response = _model.generate_content(prompt)
    return response.text.strip()