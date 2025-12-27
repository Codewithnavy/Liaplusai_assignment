from app import app

with app.test_client() as client:
    # send two user messages to build conversation
    client.post('/message', data={'message': 'I am unhappy with the service'})
    client.post('/message', data={'message': 'Actually it improved later'})
    # end the conversation and get the sentiment report
    r = client.post('/end')
    print('POST /end ->', r.status_code)
    body = r.get_data(as_text=True)
    print('Contains Conversation Sentiment Report?:', 'Conversation Sentiment Report' in body)
    # print a short excerpt including overall label if present
    if 'Conversation Sentiment Report' in body:
        idx = body.find('Conversation Sentiment Report')
        print(body[idx:idx+300])
    else:
        print('Result page snippet:')
        print(body[:800])
