# intellion/emotion_predictor.py

from typing import List, Dict

def analyze_emotion_signals(player_name: str, mentions: List[Dict[str, str]]) -> Dict:
    """
    Примитивная эвристика: на основе текста строим настроение игрока.

    mentions = [
        {"source": "Twitter", "text": "Zverev выглядит напряжённым и грустным"},
        {"source": "Reddit", "text": "Он зол после поражения"},
        ...
    ]
    """

    score = 0
    tags = []

    for m in mentions:
        text = m["text"].lower()

        if any(w in text for w in ["уверен", "в порядке", "готов", "настроен", "спокоен"]):
            score += 1
            tags.append("🟢 стабильность")

        if any(w in text for w in ["зол", "раздражён", "агрессивен", "мотивирован"]):
            score += 2
            tags.append("🔴 агрессия")

        if any(w in text for w in ["устал", "разочарован", "сломлен", "боится", "сомневается"]):
            score -= 2
            tags.append("⚠️ нестабильность")

    state = "🟡 неопределённо"
    if score >= 3:
        state = "🟢 стабильное состояние"
    elif score <= -2:
        state = "🔴 психоэмоциональный риск"

    return {
        "player": player_name,
        "total_mentions": len(mentions),
        "emotional_score": score,
        "emotional_state": state,
        "tags": list(set(tags))
    }
