import requests
import logging
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import json

# Загрузка переменных из .env
load_dotenv()

API_KEY = os.getenv("TENNIS_API_KEY")
BASE_URL = os.getenv("TENNIS_BASE", "https://api.api-tennis.com/tennis/")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# TODO: Сделать этот список настраиваемым через конфиг
TOURNAMENT_TYPES_ALLOWED = ["ATP", "WTA", "Challenger"]

# Список разрешённых букмекеров
ALLOWED_BOOKMAKERS = ["1xBet", "Fonbet"]

# Исключаем пары (doubles)
def is_singles_match(match):
    name1 = match.get("event_first_player", "").lower()
    name2 = match.get("event_second_player", "").lower()
    return ("/" not in name1 and "-" not in name1) and ("/" not in name2 and "-" not in name2)

def get_fixtures(date_str=None):
    if not API_KEY:
        logger.error("❌ API_KEY не найден. Убедись, что он задан в .env как TENNIS_API_KEY.")
        return []

    if date_str is None:
        date_str = datetime.today().strftime('%Y-%m-%d')

    url = f"{BASE_URL}?method=get_fixtures&APIkey={API_KEY}&date_start={date_str}&date_stop={date_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; IntellionBot/1.0)",
        "Accept": "application/json"
    }

    for attempt in range(3):
        try:
            logger.debug(f"[DEBUG] Попытка {attempt + 1}: GET {url}")
            response = requests.get(url, timeout=20, headers=headers)
            logger.debug(f"[DEBUG] Ответ get_fixtures: {response.text}")

            if not response.text.strip().startswith("{"):
                logger.error(f"[❌ Некорректный ответ от сервера]: {response.text}")
                return []

            data = response.json()

            if not data.get("success"):
                logger.warning("⚠️ Запрос get_fixtures не удался: success != 1")
                return []

            fixtures_raw = data.get("result", [])
            fixtures = []
            for match in fixtures_raw:
                tournament_type = match.get("event_type_type", "")
                if not any(tournament_type.startswith(t) for t in TOURNAMENT_TYPES_ALLOWED):
                    logger.debug(f"[SKIP] Турнир исключён: {tournament_type}")
                    continue
                if not is_singles_match(match):
                    logger.debug(f"[SKIP] Пары исключены: {match.get('event_first_player')} / {match.get('event_second_player')}")
                    continue
                fixtures.append({
                    "event_key": match.get("event_key"),
                    "player1": match.get("event_first_player", "Player 1"),
                    "player2": match.get("event_second_player", "Player 2"),
                    "surface": match.get("event_surface", "Hard"),
                    "start_time": match.get("event_date"),
                    "tournament_type": tournament_type
                })

            logger.info(f"📅 Получено матчей: {len(fixtures)} на дату {date_str}")
            logger.debug(f"[DEBUG] Первый матч: {json.dumps(fixtures[0], indent=2, ensure_ascii=False) if fixtures else 'Нет'}")
            return fixtures

        except requests.exceptions.Timeout:
            logger.warning(f"[⏳ Попытка {attempt + 1}] Таймаут. Повтор через 3 сек...")
            time.sleep(3)
        except Exception as e:
            logger.error(f"[❌ Ошибка получения матчей]: {e}")
            return []

    return []

def get_odds(match_key, bookmakers=None):
    if not API_KEY:
        logger.error("❌ API_KEY не найден. Убедись, что он задан в .env как TENNIS_API_KEY.")
        return {}

    url = f"{BASE_URL}?method=get_odds&APIkey={API_KEY}&match_key={match_key}"

    try:
        response = requests.get(url, timeout=10)
        logger.debug(f"[DEBUG] Ответ get_odds для {match_key}: {response.text}")

        if not response.text.strip().startswith("{"):
            logger.error(f"[❌ Некорректный ответ от сервера на get_odds]: {response.text}")
            return {}

        data = response.json()

        if not data.get("success"):
            logger.warning(f"⚠️ Запрос get_odds не удался: success != 1 для match_key={match_key}")
            return {}

        odds_data_all = data.get("result", {})
        logger.debug(f"[DEBUG] data['result']: {json.dumps(odds_data_all, indent=2)}")

        odds_raw = odds_data_all.get(str(match_key))
        if not odds_raw:
            logger.warning(f"⚠️ odds_raw пуст для match_key={match_key}")
            return {}

        def extract_odds_from_nested(market):
            market_dict = {}
            for key, sub_market in market.items():
                if isinstance(sub_market, dict):
                    values = []
                    for bkm, val in sub_market.items():
                        if bkm.lower() in [b.lower() for b in ALLOWED_BOOKMAKERS]:
                            try:
                                num_val = float(val)
                                values.append(num_val)
                            except:
                                logger.debug(f"[SKIP] Некорректный коэффициент: {val} от {bkm}")
                                continue
                    if values:
                        market_dict[key] = round(sum(values) / len(values), 2)
            return market_dict

        parsed_odds = {}
        for market_name, market_data in odds_raw.items():
            if isinstance(market_data, dict) and all(isinstance(v, dict) for v in market_data.values()):
                sub_parsed = extract_odds_from_nested(market_data)
                if sub_parsed:
                    parsed_odds[market_name] = sub_parsed
                else:
                    logger.debug(f"[SKIP] Пустой рынок: {market_name}")

        logger.debug(f"[DEBUG] Итоговые коэффициенты: {json.dumps(parsed_odds, indent=2)}")
        return parsed_odds

    except Exception as e:
        logger.error(f"[❌ Ошибка получения коэффициентов для match_key={match_key}]: {e}")
        return {}
