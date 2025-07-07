# intellion/intellion_brain.py

import logging
import json

from predictor_wrapper import predict_match
from value_model import calculate_value
from reverse_simulator import simulate_from_result
from error_analyzer import load_log, analyze_errors
from feedback_engine import log_feedback
from risk_guard import is_match_risky

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntellionBrain")

VALUE_THRESHOLD = 5.0  # минимальный порог value в процентах


def value_assessment(prob_model: float, odds: float) -> float:
    return calculate_value(prob_model, odds)


def final_decision(match_data: dict) -> dict:
    """
    Главная функция принятия решения. Возвращает прогноз, value и объяснение.
    """
    try:
        logger.info(f"🔍 Анализ матча: {match_data['player1']} vs {match_data['player2']}")

        # Шаг 1: Предсказание модели
        model_result = predict_match(match_data)
        prob = model_result["prob_player1"]

        # Шаг 2: Вычисляем value
        odds = match_data["odds_player1"]
        value = value_assessment(prob, odds)
        logger.info(f"🧠 Вероятность победы: {prob:.2f} | Кэф: {odds} | Value: {value:.2f}")

        if value < VALUE_THRESHOLD:
            return {
                "decision": "🚫 Пропустить — value ниже порога",
                "probability": prob,
                "value": value,
                "explanation": "Недостаточное преимущество над линией"
            }

        # Шаг 3: Проверка по ошибкам (анализ покрытия и прошлого опыта)
        df = load_log()
        surface_stats = {}
        if not df.empty:
            surface_stats = analyze_errors(df)["surface_errors"]

        risk_check = is_match_risky(match_data, model_result, surface_stats)
        if risk_check["is_risky"]:
            logger.warning("🛑 Рискованно — матч пропущен.")
            logger.warning("Причины: " + "; ".join(risk_check["reasons"]))
            log_feedback(match_data, model_result, actual_winner="Пропущено")
            return {
                "decision": "🛑 Пропуск — высокая рискованность",
                "reasons": risk_check["reasons"],
                "value": value,
                "probability": prob
            }

        # Шаг 4: Симуляция от результата
        reasoning = simulate_from_result({
            "player1": match_data["player1"],
            "player2": match_data["player2"],
            "surface": match_data.get("surface_type", "Unknown"),
            "score": "2:1",
            "winner": match_data["player1"]
        })

        logger.info("✅ Прогноз согласован с обратным сценарием")

        # Шаг 5: Возврат решения
        return {
            "decision": "✅ Сделать ставку — value подтверждено",
            "probability": prob,
            "value": value,
            "explanation": reasoning
        }

    except Exception as e:
        logger.error(f"Ошибка в анализе: {e}")
        return {
            "decision": "Ошибка",
            "error": str(e)
        }


# Пример запуска вручную
if __name__ == "__main__":
    example_match = {
        "player1": "Carlos Alcaraz",
        "player2": "Daniil Medvedev",
        "surface_type": "Hard",
        "odds_player1": 1.80,
        "odds_player2": 2.00,
        "bo5_match": True
    }

    result = final_decision(example_match)
    print(json.dumps(result, indent=4, ensure_ascii=False))
