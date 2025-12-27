import math
from typing import List, Dict, Any

# Lazily initialize VADER to avoid importing heavy nltk submodules at import time
_analyzer = None

def _get_analyzer():
    global _analyzer
    if _analyzer is not None:
        return _analyzer
    try:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        # Try instantiating; if lexicon missing, we'll attempt a download
        try:
            _analyzer = SentimentIntensityAnalyzer()
            return _analyzer
        except Exception:
            # attempt to download the lexicon then instantiate
            try:
                import nltk
                nltk.download('vader_lexicon')
                _analyzer = SentimentIntensityAnalyzer()
                return _analyzer
            except Exception:
                _analyzer = None
                return None
    except Exception:
        _analyzer = None
        return None


def _label_from_compound(compound: float) -> str:
    if compound >= 0.05:
        return "Positive"
    if compound <= -0.05:
        return "Negative"
    return "Neutral"


def analyze_text(text: str) -> Dict[str, Any]:
    """Return a sentiment dict for a single text."""
    if not text:
        return {"compound": 0.0, "label": "Neutral", "scores": {}}

    analyzer = _get_analyzer()
    if analyzer:
        scores = analyzer.polarity_scores(text)
        compound = scores.get("compound", 0.0)
        label = _label_from_compound(compound)
        return {"compound": compound, "label": label, "scores": scores}

    # fallback simple heuristic
    lowered = text.lower()
    positive_words = ["good", "great", "happy", "love", "excellent", "best"]
    negative_words = ["bad", "sad", "angry", "hate", "poor", "disappoint"]
    pos = sum(1 for w in positive_words if w in lowered)
    neg = sum(1 for w in negative_words if w in lowered)
    score = (pos - neg) / max(1, pos + neg)
    compound = float("{:.3f}".format(score)) if (pos + neg) > 0 else 0.0
    return {"compound": compound, "label": _label_from_compound(compound), "scores": {}}


def conversation_sentiment(history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Compute conversation-level sentiment and per-user-message sentiments.

    history: list of {'role': 'user'|'bot', 'text': str}
    """
    user_texts = [entry["text"] for entry in history if entry.get("role") == "user"]
    per_message = []
    compounds = []
    for t in user_texts:
        res = analyze_text(t)
        per_message.append({"text": t, "compound": res["compound"], "label": res["label"]})
        compounds.append(res["compound"])

    if compounds:
        avg = sum(compounds) / len(compounds)
    else:
        avg = 0.0

    overall_label = _label_from_compound(avg)

    trend = "stable"
    if compounds:
        if compounds[-1] - compounds[0] > 0.2:
            trend = "improving"
        elif compounds[0] - compounds[-1] > 0.2:
            trend = "worsening"

    return {
        "overall": {"compound": avg, "label": overall_label},
        "per_message": per_message,
        "trend": trend,
    }
