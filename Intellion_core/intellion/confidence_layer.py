# intellion/confidence_layer.py

def assess_confidence(prob_model: float, value_score: float, intuition_conf: float, scenario_plaus: float) -> float:
    """
    Объединяет 4 источника информации в единый скор доверия (confidence):
    - prob_model: вероятность по value-модели
    - value_score: рассчитанное value (например, 0.09)
    - intuition_conf: уверенность интуиции в сценарии
    - scenario_plaus: правдоподобность сценария по симулятору

    Возвращает float от 0.0 до 1.0
    """

    # Весовые коэффициенты
    w_model = 0.25
    w_value = 0.25
    w_intuition = 0.30
    w_plausibility = 0.20

    # Нормализация value: 0.07 → 0.5, 0.14+ → 1.0
    normalized_value = min(value_score / 0.14, 1.0)

    score = (
        w_model * prob_model +
        w_value * normalized_value +
        w_intuition * intuition_conf +
        w_plausibility * scenario_plaus
    )

    return round(score, 4)
