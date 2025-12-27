import os
import sys

try:
    import openai
except Exception as e:
    print('ERROR: openai library not installed:', e)
    sys.exit(2)

KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_KEY')
if not KEY:
    print('ERROR: OPENAI_API_KEY not set in environment')
    sys.exit(3)

openai.api_key = KEY
model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

system_prompt = "You are a concise assistant used for a quick local connection test. Reply briefly."
user_prompt = "Hello — this is a connectivity test. Reply with one short sentence confirming you are available."

try:
    # Try old-style ChatCompletion (backwards-compatible). Newer openai packages use a different client.
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{'role':'system','content':system_prompt}, {'role':'user','content':user_prompt}],
            max_tokens=60,
            temperature=0.2,
        )
        choice = resp.get('choices', [])[0]
        content = choice.get('message', {}).get('content', '')
    except Exception:
        # Try the new OpenAI client interface (openai>=1.0.0)
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model,
            messages=[{'role':'system','content':system_prompt}, {'role':'user','content':user_prompt}],
            max_tokens=60,
            temperature=0.2,
        )
        # new response shape
        content = resp.choices[0].message.content
    print('---OPENAI-REPLY-START---')
    print(content.strip())
    print('---OPENAI-REPLY-END---')
    sys.exit(0)
except Exception as e:
    print('ERROR: OpenAI request failed:', repr(e))
    sys.exit(4)
