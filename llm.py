import os
from typing import List, Dict

try:
    import openai
except Exception:
    openai = None


def _get_api_key():
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")


def _get_model():
    return os.environ.get("OPENAI_MODEL", os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo"))


def _local_fallback(user_text: str) -> str:
    lowered = user_text.lower()
    if any(w in lowered for w in ["help", "issue", "error", "problem"]):
        return "I'm sorry to hear that — can you tell me more so I can help?"
    if any(w in lowered for w in ["thanks", "thank you", "appreciate"]):
        return "You're welcome — glad I could help."
    if any(w in lowered for w in ["price", "cost", "subscribe"]):
        return "I can share pricing details — what specifically would you like to know?"
    return "Thanks for sharing — tell me more or press End Conversation when done."


def _build_messages(history: List[Dict[str, str]], user_text: str) -> List[Dict[str, str]]:
    system_prompt = "You are a helpful friendly assistant that answers concisely."
    messages = [{"role": "system", "content": system_prompt}]
    recent = history[-8:] if len(history) > 8 else history
    for entry in recent:
        role = "user" if entry.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": entry.get("text", "")})
    messages.append({"role": "user", "content": user_text})
    return messages


def generate_reply_via_llm(history: List[Dict[str, str]], user_text: str, api_key: str = None, model: str = None) -> str:
    """Generate a reply using OpenAI if available; otherwise return a local fallback."""
    key = api_key or _get_api_key()
    if not openai or not key:
        return "(LLM unavailable) " + _local_fallback(user_text)

    model = model or _get_model()
    messages = _build_messages(history, user_text)

    # Try old client then new client
    try:
        openai.api_key = key
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        choice = resp.get("choices", [])[0]
        return (choice.get("message", {}) or {}).get("content", "").strip()
    except Exception:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return "(LLM error) " + _local_fallback(user_text)
