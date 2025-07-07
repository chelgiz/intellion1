# intellion/got_writer.py

import os
import openai
from dotenv import load_dotenv
from models import GPTInsightRequest

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

INTELLION_PROMPT = """
Ты — Интеллион, цифровой интеллект нового поколения.
Говоришь логично, спокойно, без воды. Стиль — как у мастера стратегий.

Используй структуру:
- Факт
- Причина
- Следствие
- Вывод

Если задан режим 'reverse' — мысли от результата к причинам.
Если задан 'value_summary' — оценивай расхождение model vs implied probability.
Если задан 'fractal' — ищи скрытые повторяющиеся паттерны.

Ты не предполагаешь. Ты реконструируешь.
"""

def generate_insight(data: GPTInsightRequest) -> str:
    """
    Генерирует аналитический вывод от имени Intellion.
    data: объект GPTInsightRequest с полями mode и context
    """
    try:
        messages = [
            {"role": "system", "content": INTELLION_PROMPT},
            {"role": "user", "content": f"[Режим: {data.mode}]\n\n{data.context}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",  # или gpt-3.5-turbo при ограничениях
            messages=messages,
            temperature=0.6
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[Ошибка генерации анализа: {e}]"
