"""
SentimentAI - Analyse de sentiment simple basée sur des lexiques.
"""

POSITIVE_WORDS = {
    "bon", "bien", "super", "excellent", "génial", "parfait", "magnifique",
    "formidable", "fantastique", "merveilleux", "good", "great", "excellent",
    "amazing", "wonderful", "fantastic", "happy", "love", "best", "awesome",
    "bravo", "top", "cool", "nice", "positive", "incroyable", "sublime",
}

NEGATIVE_WORDS = {
    "mauvais", "nul", "horrible", "terrible", "affreux", "catastrophique",
    "déplorable", "médiocre", "décevant", "bad", "terrible", "awful",
    "horrible", "worst", "hate", "ugly", "poor", "negative", "nul",
    "décevant", "lamentable", "pathétique", "raté",
}


def preprocess(text: str) -> list[str]:
    """Nettoie et tokenise le texte en minuscules."""
    if not isinstance(text, str):
        raise TypeError(f"Le texte doit être une chaîne, reçu : {type(text)}")
    text = text.lower()
    # Supprime la ponctuation simple
    for char in ".,!?;:\"'()[]{}":
        text = text.replace(char, " ")
    return [word for word in text.split() if word]


def analyze(text: str) -> dict:
    """
    Analyse le sentiment d'un texte.

    Retourne un dictionnaire avec :
        - label : 'positive', 'negative' ou 'neutral'
        - score : float entre -1.0 (très négatif) et 1.0 (très positif)
        - positive_count : nombre de mots positifs détectés
        - negative_count : nombre de mots négatifs détectés
    """
    words = preprocess(text)

    if not words:
        return {"label": "neutral", "score": 0.0,
                "positive_count": 0, "negative_count": 0}

    positive_count = sum(1 for w in words if w in POSITIVE_WORDS)
    negative_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = positive_count + negative_count

    if total == 0:
        score = 0.0
        label = "neutral"
    else:
        score = round((positive_count - negative_count) / total, 4)
        if score > 0:
            label = "positive"
        elif score < 0:
            label = "negative"
        else:
            label = "neutral"

    return {
        "label": label,
        "score": score,
        "positive_count": positive_count,
        "negative_count": negative_count,
    }


def batch_analyze(texts: list) -> list[dict]:
    """Analyse une liste de textes et retourne une liste de résultats."""
    if not isinstance(texts, list):
        raise TypeError("batch_analyze attend une liste de textes")
    return [analyze(text) for text in texts]


def get_summary(results: list[dict]) -> dict:
    """Retourne un résumé statistique d'une liste de résultats d'analyse."""
    if not results:
        return {"total": 0, "positive": 0, "negative": 0, "neutral": 0,
                "average_score": 0.0}

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for r in results:
        counts[r["label"]] += 1

    avg_score = round(sum(r["score"] for r in results) / len(results), 4)

    return {
        "total": len(results),
        "positive": counts["positive"],
        "negative": counts["negative"],
        "neutral": counts["neutral"],
        "average_score": avg_score,
    }
