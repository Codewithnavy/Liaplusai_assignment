# Chatbot with Conversation-Level Sentiment Analysis

This project implements a simple chatbot with conversation-level sentiment analysis (Tier 1) and per-message sentiment (Tier 2).

**Status**
- Tier 1: Implemented — full conversation sentiment at "End Conversation".
- Tier 2: Implemented — per-user-message sentiment listed in the report and a simple trend analysis.

**Technologies**
- Python 3.8+
- Flask for web UI
- NLTK VADER for sentiment scoring (fallback heuristic available)
- Bootstrap 5 + Chart.js for a clean UI and trend visualization

How to run (Windows PowerShell):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# NLTK may need the vader_lexicon; the app attempts to download it automatically.
python app.py
```

Open http://127.0.0.1:5000 in your browser.

LLM (OpenAI) integration
- Set your OpenAI API key in the environment variable `OPENAI_API_KEY` or copy `.env.example` to `.env` and update the key.
- The app will use the OpenAI Chat API to generate more natural chatbot replies when the key is available. The repository never stores your secret key — do not commit it.


Design & sentiment logic
- Each user message is analyzed by NLTK VADER when available. A compound score is used to label messages: compound >= 0.05 is Positive, <= -0.05 is Negative, otherwise Neutral.
- Conversation-level sentiment is the mean compound score across all user messages; the same thresholds are used to assign an overall label.
- A small trend heuristic reports whether the mood is improving/worsening/stable.

Project structure
- `app.py` — Flask application and minimal chatbot logic
- `sentiment.py` — sentiment helpers and conversation-level aggregator
- `templates/` — HTML templates for chat and report
- `static/` — CSS and assets
- `tests/` — unit tests for sentiment functions

Tests
Run tests with:

```powershell
pytest -q
```

Notes
- The chatbot reply logic is intentionally simple and modular so it can be replaced with an LLM or other model.
- For production, set `FLASK_SECRET` to a secure value and run behind a WSGI server.
