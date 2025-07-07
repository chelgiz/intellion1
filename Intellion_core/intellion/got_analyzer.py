# intellion/got_analyzer.py

import openai
import os
from dotenv import load_dotenv
import json
import re

# Загрузка переменных окружения из .env
load_dotenv()

# Установка ключа OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_player_state(player_name: str, surface: str, news: list[str]) -> dict:
    if not news:
        return {
            "motivation": "unknown",
            "physical": "unknown",
            "emotion": "unknown",
            "impact_score": 0.0
        }

    news_text = "\n".join(f"- {n}" for n in news[:5])

    prompt = f"""
Игрок: {player_name}
Покрытие: {surface}
Новости:
{news_text}

На основе новостей оцени следующие параметры игрока:

1. Мотивация (низкая / средняя / высокая)
2. Физическое состояние (плохое / среднее / хорошее)
3. Эмоциональное состояние (нестабильное / спокойное / заряженное)
4. Влияние всех этих факторов на результат матча (по шкале от 0.0 до 1.0)

Ответ в формате JSON со следующими полями:
- motivation
- physical
- emotion
- impact_score (float от 0.0 до 1.0)
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content

        # Попытка парсинга JSON из текста
        json_text = re.search(r"{.*}", content, re.DOTALL)
        if json_text:
            data = json.loads(json_text.group(0))
            return {
                "motivation": data.get("motivation", "unknown"),
                "physical": data.get("physical", "unknown"),
                "emotion": data.get("emotion", "unknown"),
                "impact_score": float(data.get("impact_score", 0.0))
            }
    except Exception as e:
        print(f"[GPT error]: {e}")

    return {
        "motivation": "unknown",
        "physical": "unknown",
        "emotion": "unknown",
        "impact_score": 0.0
    }
