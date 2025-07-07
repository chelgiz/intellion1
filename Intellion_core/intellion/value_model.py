# intellion/value_model.py

def implied_probability(odds: float) -> float:
    """
    Перевод коэффициента в вероятностную оценку.
    Пример: 2.00 → 0.50
    """
    if odds <= 0:
        return 0.0
    return round(1 / odds, 4)


def calculate_value(prob_model: float, odds: float) -> float:
    """
    Рассчитывает value как разницу между модельной вероятностью и рыночной.
    """
    prob_market = implied_probability(odds)
    value = prob_model - prob_market
    return round(value, 4)


def calculate_probability(match: dict) -> dict:
    """
    Заглушка: возвращает условные вероятности по рынкам для расчёта value.
    В будущем сюда вставляется ML или логика интуиции.
    """
    probs = {}

    home_odds = match.get("home_odds")
    away_odds = match.get("away_odds")

    if home_odds and away_odds:
        total = (1 / home_odds) + (1 / away_odds)
        probs["match_winner_home"] = round((1 / home_odds) / total, 4)
        probs["match_winner_away"] = round((1 / away_odds) / total, 4)

    # Примерная заглушка для других рынков
    if match.get("totals"):
        for line, data in match["totals"].items():
            if isinstance(data, dict) and "odds" in data:
                probs[f"total_over_{line}"] = 0.52
                probs[f"total_under_{line}"] = 0.48

    if match.get("handicaps"):
        for line, data in match["handicaps"].items():
            if isinstance(data, dict) and "odds" in data:
                probs[f"handicap_{line}"] = 0.50

    if match.get("individual_totals"):
        for player_key, totals in match["individual_totals"].items():
            for line, data in totals.items():
                if isinstance(data, dict) and "odds" in data:
                    probs[f"{player_key.lower()}_total_over_{line}"] = 0.51
                    probs[f"{player_key.lower()}_total_under_{line}"] = 0.49

    if match.get("tiebreak"):
        for option, data in match["tiebreak"].items():
            if option.lower() == "yes":
                probs["tiebreak_yes"] = 0.35
            elif option.lower() == "no":
                probs["tiebreak_no"] = 0.65

    return probs
