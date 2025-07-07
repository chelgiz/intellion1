# intellion/intuition_engine.py

def generate_hypotheses(match: dict) -> list[dict]:
    """
    Генерирует возможные исходы матча в зависимости от формата (BO3 или BO5).
    """
    best_of = int(match.get("best_of", 3))  # по умолчанию BO3

    if best_of == 3:
        return [
            {"winner": "1", "score": "2-0"},
            {"winner": "1", "score": "2-1"},
            {"winner": "2", "score": "2-0"},
            {"winner": "2", "score": "2-1"},
        ]
    else:
        return [
            {"winner": "1", "score": "3-0"},
            {"winner": "1", "score": "3-1"},
            {"winner": "1", "score": "3-2"},
            {"winner": "2", "score": "3-0"},
            {"winner": "2", "score": "3-1"},
            {"winner": "2", "score": "3-2"},
        ]


def evaluate_hypothesis(hypothesis: dict, match: dict) -> float:
    """
    Эвристика оценки уверенности в гипотезе.
    Будет заменено на симуляции + ML.
    """
    winner = hypothesis["winner"]
    score = hypothesis["score"]
    court = match.get("surface_type", "Hard")
    best_of = int(match.get("best_of", 3))

    if best_of == 3:
        if winner == "1" and score == "2-0":
            return 0.65 if court == "Clay" else 0.60
        if winner == "1" and score == "2-1":
            return 0.58
        if winner == "2" and score == "2-0":
            return 0.55
        if winner == "2" and score == "2-1":
            return 0.52
    else:
        if winner == "1" and score == "3-0":
            return 0.63
        if winner == "1" and score == "3-1":
            return 0.60
        if winner == "1" and score == "3-2":
            return 0.57
        if winner == "2" and score == "3-0":
            return 0.54
        if winner == "2" and score == "3-1":
            return 0.52
        if winner == "2" and score == "3-2":
            return 0.50

    return 0.5


def get_best_scenario(match: dict) -> dict:
    """
    Выбирает наиболее вероятную гипотезу.
    """
    hypotheses = generate_hypotheses(match)
    rated = [(hyp, evaluate_hypothesis(hyp, match)) for hyp in hypotheses]
    rated.sort(key=lambda x: x[1], reverse=True)

    return {
        "hypothesis": rated[0][0],
        "confidence": rated[0][1]
    }


def predict_outcome(match: dict, context: dict = None) -> dict:
    """
    Возвращает финальное интуитивное предсказание и обоснование.
    """
    best = get_best_scenario(match)
    hyp = best["hypothesis"]
    confidence = best["confidence"]

    winner = match["player1"] if hyp["winner"] == "1" else match["player2"]

    reasoning = "Интуитивно: {} победит со счётом {} на {}. Уверенность: {:.0f}%".format(
        winner, hyp["score"], match.get("surface_type", "Hard"), confidence * 100
    )

    return {
        "winner": winner,
        "score_pred": hyp["score"],
        "confidence": confidence,
        "reasoning": reasoning
    }
