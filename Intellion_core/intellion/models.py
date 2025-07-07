# intellion/models.py

from pydantic import BaseModel

class GPTInsightRequest(BaseModel):
    mode: str  # Например: 'reverse', 'value_summary', 'fractal'
    context: str  # Контекст анализа: описание матча, данных, выводов
