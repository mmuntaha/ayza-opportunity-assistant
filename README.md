# Opportunity Assistant

An AI agent that stops good opportunities from dying in your "saved posts."

## The problem

You save job posts, volunteer opportunities, and outreach contacts (from LinkedIn,
Instagram, wherever) meaning to apply later. Later never comes. The links pile up
unopened.

## What it does

You keep a simple Google Sheet of opportunities. The agent:

1. **Reads** each row in the Sheet
2. **Branches** based on what the opportunity needs:
   - **Outreach** (you need to email someone) → drafts a personalized email and
     saves it as a real **Gmail draft** (never auto-sent — you review and hit send)
   - **Application** (a form with specific questions) → drafts tailored answers
     to those exact questions, using your background info, and writes them back
     into the **same Sheet** in a new column
3. **Reminds** you — sends a **Slack** message for any opportunity with an
   approaching deadline, so it doesn't get buried again

## External apps connected (3)

| App | Used for | Auth method |
|---|---|---|
| Google Sheets | Source of truth: your opportunity list, and destination for drafted answers | OAuth (Google Cloud credentials) |
| Gmail | Saves personalized outreach emails as drafts | OAuth (same Google credentials) |
| Slack | Sends deadline reminder messages | Bot token |

Claude (Anthropic API) is the reasoning engine that reads each row and decides
what to write — this is what makes it an *agent* rather than a template filler.

---

## Setup instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google (Sheets + Gmail)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → create a
   new project (any name).
2. Go to **APIs & Services → Library** → enable **Google Sheets API** and
   **Gmail API**.
3. Go to **APIs & Services → Credentials** → **Create Credentials → OAuth client ID**.
   - If prompted, configure the consent screen first (choose "External", fill in
     app name + your email, skip scopes/test users screens by clicking through).
   - Application type: **Desktop app**. Name it anything.
4. Download the JSON file it gives you. Rename it to `credentials.json` and put
   it in this project's root folder.
5. The first time you run the app, a browser window will open asking you to log
   in and approve access. After that, a `token.json` is saved so you won't have
   to log in again.

### 3. Set up your Google Sheet

1. Create a new Google Sheet.
2. Name the first sheet tab `Opportunities` and add these column headers in row 1:

   `Link | Type | Contact Name | Contact Email | Questions | Deadline | Status | Drafted Answers`

   - `Type` should be either `outreach` or `application`
   - `Questions` (only for `application` rows): paste the actual questions,
     separated by `|` — e.g. `Why do you want to volunteer? | Describe relevant experience`
   - `Deadline`: format `YYYY-MM-DD`
   - Leave `Status` and `Drafted Answers` blank — the agent fills these in

3. Copy the Sheet's ID from its URL:
   `https://docs.google.com/spreadsheets/d/THIS_PART_IS_THE_ID/edit`

### 4. Set up Slack

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** →
   **From scratch**. Name it, pick your workspace.
2. Go to **OAuth & Permissions** → under **Scopes → Bot Token Scopes**, add:
   `chat:write` and `channels:read`.
3. Scroll up, click **Install to Workspace**, approve.
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`).
5. In Slack, go to the channel you want reminders in and type
   `/invite @YourBotName`.

### 5. Set up Claude (Anthropic API)

1. Get an API key from [console.anthropic.com](https://console.anthropic.com).

### 6. Fill in your `.env` file

Copy `.env.example` to `.env` and fill in every value:

```bash
cp .env.example .env
```

### 7. Tell the agent about yourself

Edit `about_me.txt` with a short paragraph about your background, skills, and
what you're looking for. This is what the agent uses to personalize every
email and answer.

### 8. Run it

```bash
python main.py
```

---

## Reliability testing

We tested the agent against these scenarios (see `test_reliability.py` and
`TESTING.md` for full details and console output):

1. **Normal outreach row** — correct email drafted and saved to Gmail, status
   updated in Sheet.
2. **Normal application row with multiple questions** — each question answered
   individually and written back to the Sheet, not merged into one blob.
3. **Missing/malformed data** (empty Questions column on an `application` row) —
   agent skips the row, logs a clear warning, and does NOT crash or produce a
   blank/garbage draft.
4. **Invalid Slack channel or bad token** — caught and logged as an error with
   a clear message; the rest of the pipeline (Sheets/Gmail) still completes.
5. **Deadline in the past vs. future** — only future/near-term deadlines trigger
   a Slack reminder, to avoid spamming stale rows.
6. **Re-running on the same sheet** — rows already marked `Status: Done` are
   skipped, so nothing gets double-drafted or double-messaged.

## Demo video

[(https://youtu.be/F50js0LB7r4)]
