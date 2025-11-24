import os
from typing import List, Dict

try:
    import openai
except Exception:
    openai = None


def _get_api_key():
    # prefer environment variable
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")


def generate_reply_via_llm(history: List[Dict[str, str]], user_text: str) -> str:
    """Generate a reply using the configured OpenAI key. Returns a fallback reply if unavailable."""
    api_key = _get_api_key()
    if not openai or not api_key:
        return "(LLM unavailable) " + ("Thanks for sharing — tell me more or press End Conversation when done.")

    openai.api_key = api_key

    # Build a compact chat context: include system prompt + last few turns
    system_prompt = "You are a helpful friendly assistant that answers concisely."
    messages = [{"role": "system", "content": system_prompt}]

    # include up to last 8 messages
    recent = history[-8:] if len(history) > 8 else history
    for entry in recent:
        role = "user" if entry.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": entry.get("text", "")})

    # add the current user turn explicitly
    messages.append({"role": "user", "content": user_text})

    try:
        resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=150, temperature=0.7)
        choice = resp.get("choices", [])[0]
        return choice.get("message", {}).get("content", "")
    except Exception:
        return "(LLM error) " + "Thanks for sharing — tell me more or press End Conversation when done."
import os
from typing import List, Dict

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


def _local_fallback(user_text: str, history: List[Dict[str, str]]) -> str:
    lowered = user_text.lower()
    if any(w in lowered for w in ["help", "issue", "error", "problem"]):
        return "I'm sorry to hear that — can you tell me more so I can help?"
    if any(w in lowered for w in ["thanks", "thank you", "appreciate"]):
        return "You're welcome — glad I could help."
    if any(w in lowered for w in ["price", "cost", "subscribe"]):
        return "I can share pricing details — what specifically would you like to know?"
    return "Thanks for sharing — tell me more or press End Conversation when done."


def get_reply(user_text: str, history: List[Dict[str, str]]) -> str:
    """Return a reply string. If `OPENAI_API_KEY` is set, call OpenAI Chat API.

    This function keeps a simple, safe fallback when OpenAI is not configured
    or an error occurs.
    """
    if not OPENAI_KEY:
        return _local_fallback(user_text, history)

    try:
        import openai
        openai.api_key = OPENAI_KEY

        # build messages: system prompt + last N conversation entries
        system_prompt = (
            "You are a concise, helpful customer-support assistant. Keep replies brief, "
            "ask clarifying questions when needed, and be empathetic."
        )

        messages = [{"role": "system", "content": system_prompt}]
        # include up to last 10 messages for context
        context = (history or [])[-20:]
        for entry in context:
            role = "user" if entry.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": entry.get("text", "")})

        # add the new user message
        messages.append({"role": "user", "content": user_text})

        resp = openai.ChatCompletion.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=150,
            temperature=0.6,
        )
        content = resp.choices[0].message.content.strip()
        return content
    except Exception:
        return _local_fallback(user_text, history)
