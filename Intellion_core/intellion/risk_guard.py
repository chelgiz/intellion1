# intellion/risk_guard.py

def is_match_risky(match: dict, prediction: dict, surface_stats: dict = None) -> dict:
    """
    Примитивный фильтр риска:
    - проверяет покрытие
    - сравнивает value с порогом
    - проверяет наличие травм и нестабильности (в будущем)

    Возвращает:
    {
        "is_risky": True/False,
        "reasons": [...]
    }
    """
    reasons = []

    surface = match.get("surface_type", "Unknown")
    if surface_stats and surface in surface_stats and surface_stats[surface] > 3:
        reasons.append(f"Высокая ошибка на покрытии: {surface} ({surface_stats[surface]})")

    value = prediction.get("value", 0)
    if value < 0.05:
        reasons.append(f"Слишком низкое value: {value:.2f}")

    return {
        "is_risky": len(reasons) > 0,
        "reasons": reasons
    }
