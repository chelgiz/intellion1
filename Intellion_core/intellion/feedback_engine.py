# intellion/feedback_engine.py

import json
from pathlib import Path
from datetime import datetime

LEARNING_LOG = Path("logs/learning_log.json")
LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)

def feedback_correction(model_output: str, actual_result: str) -> float:
    """
    Возвращает корректировку к модели на основе различия между прогнозом и фактом.
    Используется для накопления ошибок и обучения модели в будущем.
    """
    if model_output == actual_result:
        delta = 0.0
    else:
        delta = -0.1  # Условная корректировка за ошибку

    log_feedback(model_output, actual_result, delta)
    return delta

def log_feedback(prediction: str | dict, actual: str, adjustment: float):
    """
    Сохраняет в журнал информацию о корректировке и прогнозе.
    prediction может быть как строкой (например, имя победителя), так и dict с доп. данными.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "prediction": prediction,
        "actual_result": actual,
        "adjustment": adjustment
    }

    # Загружаем или создаём журнал
    if LEARNING_LOG.exists():
        with open(LEARNING_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry)

    # Сохраняем обратно
    with open(LEARNING_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
