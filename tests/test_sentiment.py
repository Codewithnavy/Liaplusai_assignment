from sentiment import analyze_text, conversation_sentiment


def test_analyze_positive():
    res = analyze_text("I am very happy and this is great")
    assert res["label"] in ("Positive", "Neutral")


def test_analyze_negative():
    res = analyze_text("This is terrible and I hate it")
    assert res["label"] in ("Negative", "Neutral")


def test_conversation_sentiment_empty():
    rpt = conversation_sentiment([])
    assert rpt["overall"]["label"] == "Neutral"
