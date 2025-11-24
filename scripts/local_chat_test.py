from app import app

with app.test_client() as client:
    # send a user message
    r = client.post('/message', data={'message': 'Hello test'}, follow_redirects=True)
    print('POST /message ->', r.status_code)
    body = r.get_data(as_text=True)
    # show whether user message and bot reply appear in the HTML
    user_present = 'Hello test' in body
    print('User text present in rendered page?:', user_present)
    # heuristically look for fallback or bot text
    has_bot = 'Thanks for sharing' in body or 'I\'m sorry to hear' in body or 'fallback' in body
    print('Bot reply present?:', has_bot)
    # print a short excerpt around the user message
    if user_present:
        idx = body.index('Hello test')
        print(body[idx-200:idx+200])
    else:
        print('Rendered page snippet:')
        print(body[:800])
