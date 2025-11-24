import os
import openai

# Simple smoke test: send a tiny prompt and print a trimmed reply
MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
KEY = os.environ.get("OPENAI_API_KEY")
if not KEY:
    raise SystemExit("OPENAI_API_KEY not set")
openai.api_key = KEY

resp = openai.ChatCompletion.create(model=MODEL, messages=[{"role":"user","content":"Say 'pong'"}], max_tokens=10)
text = resp.get('choices', [])[0].get('message', {}).get('content', '')
print(text.strip())
