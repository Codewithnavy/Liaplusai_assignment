from flask import Flask, render_template, request, redirect, url_for, session
from sentiment import analyze_text, conversation_sentiment
from llm import generate_reply_via_llm
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-for-production")


@app.route("/", methods=["GET"])
def index():
    history = session.get("history", [])
    return render_template("index.html", history=history)


@app.route("/message", methods=["POST"])
def message():
    user_text = request.form.get("message", "").strip()
    if not user_text:
        return redirect(url_for("index"))

    history = session.get("history", [])
    history.append({"role": "user", "text": user_text})
    # Try LLM first, then fallback to local rule-based reply
    bot_reply = generate_reply_via_llm(history, user_text)
    if not bot_reply or bot_reply.startswith("(LLM") or bot_reply.startswith("(LLM error"):
        bot_reply = generate_reply_fallback(user_text)
    history.append({"role": "bot", "text": bot_reply})

    session["history"] = history
    return redirect(url_for("index"))


def generate_reply_fallback(user_text: str) -> str:
    lowered = user_text.lower()
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
