from flask import Flask, render_template, request, redirect, url_for, session
from sentiment import analyze_text, conversation_sentiment
from llm import generate_reply_via_llm
import os
from flask import flash
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-for-production")


@app.route("/", methods=["GET"])
def index():
    history = session.get("history", [])
    # compute model and LLM availability for header indicator
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    llm_lib = False
    try:
        import openai as _openai  # noqa: F401
        llm_lib = True
    except Exception:
        llm_lib = False

    available = llm_lib and bool(key)
    return render_template("index.html", history=history, model=model, llm_available=available)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        model = request.form.get("model", "gpt-3.5-turbo").strip()
        if api_key:
            # set for current process only; do not persist to disk
            os.environ["OPENAI_API_KEY"] = api_key
        if model:
            os.environ["OPENAI_MODEL"] = model
        flash("Settings updated for this running instance.", "success")
        return redirect(url_for("settings"))

    current_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    return render_template("settings.html", model=current_model)


@app.route("/status", methods=["GET"])
def status():
    """Return a simple status page showing model & LLM availability."""
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    llm_lib = False
    try:
        import openai as _openai  # noqa: F401
        llm_lib = True
    except Exception:
        llm_lib = False

    available = llm_lib and bool(key)
    return render_template("status.html", model=model, available=available, has_key=bool(key), llm_lib=llm_lib)


@app.route("/troubleshoot", methods=["GET"])
def troubleshoot():
    """Simple troubleshooting page with quick checks."""
    return render_template("troubleshoot.html")


@app.route("/message", methods=["POST"])
def message():
    # accept JSON or form-encoded bodies
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        user_text = (payload.get('message') or '').strip()
    else:
        user_text = request.form.get("message", "").strip()

    if not user_text:
        # if AJAX or JSON request, return JSON error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            from flask import jsonify
            return jsonify({'error': 'empty_message'}), 400
        return redirect(url_for("index"))

    history = session.get("history", [])
    # attach an ISO timestamp for each message
    ts = datetime.utcnow().isoformat() + "Z"
    history.append({"role": "user", "text": user_text, "ts": ts})
    # Try LLM first, then fallback to local rule-based reply
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    bot_reply = generate_reply_via_llm(history, user_text, api_key=api_key, model=model)
    used_model = None
    if not bot_reply or bot_reply.startswith("(LLM") or bot_reply.startswith("(LLM error"):
        bot_reply = generate_reply_fallback(user_text)
        used_model = "fallback"
    else:
        used_model = model
    # Log the produced reply for debugging (appears in the server console)
    try:
        app.logger.info(f"[chat] user={user_text!r} bot_reply={bot_reply!r} used_model={used_model!r}")
    except Exception:
        print(f"[chat] user={user_text!r} bot_reply={bot_reply!r} used_model={used_model!r}")
    history.append({"role": "bot", "text": bot_reply, "model": used_model, "ts": datetime.utcnow().isoformat() + "Z"})

    session["history"] = history
    # If this is an AJAX request, return JSON with the new bot reply and timestamps
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        from flask import jsonify
        return jsonify({
            'user': {'text': user_text, 'ts': ts},
            'bot': {'text': bot_reply, 'model': used_model, 'ts': datetime.utcnow().isoformat() + 'Z'}
        })

    return redirect(url_for("index"))


def generate_reply_fallback(user_text: str) -> str:
    lowered = user_text.lower()
    # common greeting detection
    greetings = ["hi", "hello", "hey", "hey there", "good morning", "good afternoon", "good evening"]
    if any(lowered == g or lowered.startswith(g + " ") or (g in lowered and len(lowered.split())<=3) for g in greetings):
        options = [
            "Hi — how are you? How can I assist you today?",
            "Hello! I'm here to help — how can I assist you?",
            "Hey there — what can I do for you today?",
            "Hi! Hope you're well. How can I help?"
        ]
        return random.choice(options)
    if any(w in lowered for w in ["help", "issue", "error", "problem"]):
        return "I'm sorry to hear that — can you tell me more so I can help?"
    if any(w in lowered for w in ["thanks", "thank you", "appreciate"]):
        return "You're welcome — glad I could help."
    if any(w in lowered for w in ["price", "cost", "subscribe"]):
        return "I can share pricing details — what specifically would you like to know?"
    return "Thanks for sharing — tell me more or press End Conversation when done."


@app.route("/end", methods=["POST"])
def end_conversation():
    history = session.get("history", [])
    report = conversation_sentiment(history)
    session.pop("history", None)
    return render_template("result.html", report=report, history=history)


@app.route("/clear", methods=["POST"])
def clear_conversation():
    session.pop("history", None)
    flash("Conversation cleared.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
