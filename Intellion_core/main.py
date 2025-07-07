import logging
from datetime import datetime
import json
import time

from intellion.api import get_fixtures, get_odds
from intellion.value_model import calculate_probability, calculate_value
from intellion.intuition_engine import get_best_scenario
from intellion.reverse_simulator import simulate_path_to_score
from intellion.confidence_layer import assess_confidence
from intellion.news_fetcher import get_news
from intellion.got_analyzer import analyze_player_state


def load_model_config(path="intellion/model_config.json") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[❗️Ошибка чтения конфигурации]: {e}")
        return {"min_confidence": 0.75, "min_value": 0.07}

import os
os.environ["PYTHON_LOG_LEVEL"] = "DEBUG"

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)

def run_analysis():
    logging.info("🚀 Старт анализа от Интеллиона")

    config = load_model_config()
    min_confidence = config.get("min_confidence", 0.75)
    min_value = config.get("min_value", 0.07)
    logging.info(f"⚙️ Порог: Confidence ≥ {min_confidence}, Value ≥ {min_value}")

    today = datetime.now().strftime("%Y-%m-%d")
    fixtures = get_fixtures(today)

    if not fixtures:
        logging.info("❌ Нет матчей на сегодня")
        return

    logging.info(f"📅 Найдено матчей: {len(fixtures)}")

    value_bets = []

    for match in fixtures:
        event_key = match.get("event_key")
        if not event_key:
            continue

        try:
            odds_data = get_odds(event_key, bookmakers=["1xbet", "fonbet"])
        except Exception as e:
            logging.error(f"[❌ Ошибка получения коэффициентов для match_key={event_key}]: {e}")
            time.sleep(1.5)
            continue

        if not odds_data:
            logging.warning("⚠️ Пропуск — пустой odds_data")
            continue

        p1 = match.get("player1", "Player 1")
        p2 = match.get("player2", "Player 2")
        court = match.get("surface", "Hard")

        logging.info(f"🎾 Матч: {p1} vs {p2} | key={event_key}")
        logging.debug(f"🔎 odds_data: {odds_data}")

        # Подготовка коэффициентов для value_model
        home_odds = odds_data.get("Home/Away", {}).get("Home")
        away_odds = odds_data.get("Home/Away", {}).get("Away")

        match["home_odds"] = home_odds
        match["away_odds"] = away_odds
        match["totals"] = odds_data.get("Over/Under by Games in Match", {})
        match["handicaps"] = odds_data.get("Asian Handicap (Games)", {})
        match["individual_totals"] = {
            "home": odds_data.get("Total - Home", {}),
            "away": odds_data.get("Total - Away", {})
        }
        match["tiebreak"] = odds_data.get("Tiebreak in Match", {})

        prediction = calculate_probability(match)
        if not prediction:
            logging.warning("⚠️ Пропуск — нет прогноза")
            continue

        p1_news = get_news(p1)
        p2_news = get_news(p2)
        p1_state = analyze_player_state(p1, court, p1_news)
        p2_state = analyze_player_state(p2, court, p2_news)

        logging.info(f"📰 {p1} | мотивация: {p1_state['motivation']}, физика: {p1_state['physical']}, эмоции: {p1_state['emotion']}, влияние: {p1_state['impact_score']:.2f}")
        logging.info(f"📰 {p2} | мотивация: {p2_state['motivation']}, физика: {p2_state['physical']}, эмоции: {p2_state['emotion']}, влияние: {p2_state['impact_score']:.2f}")

        scenario = get_best_scenario(match)
        simulation = simulate_path_to_score(scenario["hypothesis"], match)

        for market, model_prob in prediction.items():
            odds = odds_data.get(market)
            if not odds:
                continue

            try:
                value = calculate_value(model_prob, odds)
                avg_impact = (p1_state.get("impact_score", 0.5) + p2_state.get("impact_score", 0.5)) / 2
                adjusted_model_prob = model_prob * (1 - avg_impact)

                confidence_score = assess_confidence(
                    prob_model=adjusted_model_prob,
                    value_score=value,
                    intuition_conf=scenario["confidence"],
                    scenario_plaus=simulation["plausibility"]
                )

                if confidence_score >= min_confidence and value >= min_value:
                    logging.info(f"🔥 Ставка одобрена! CONFIDENCE: {confidence_score:.2f}")
                    value_bets.append({
                        "match": match,
                        "market": market,
                        "probability": model_prob,
                        "odds": odds,
                        "value": value,
                        "confidence": confidence_score
                    })
                else:
                    logging.info(f"⚠️ Отклонено: confidence {confidence_score:.2f}, value {value:.2f}")

            except Exception as e:
                logging.warning(f"⚠️ Ошибка в расчёте: {e}")
                continue

    if value_bets:
        logging.info(f"✅ Найдено value-ставок: {len(value_bets)}")
        for bet in value_bets:
            m = bet["match"]
            logging.info(f"🎯 {m.get('player1')} vs {m.get('player2')} | {bet['market']} | Кэф: {bet['odds']} | Модель: {bet['probability']*100:.1f}% | Value: {bet['value']*100:.2f}% | Confidence: {bet['confidence']:.2f}")
    else:
        logging.info("❌ Value-ставки не найдены или confidence слишком низкий.")


if __name__ == "__main__":
    run_analysis()
