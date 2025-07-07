# intellion/error_analyzer.py

import json
import pandas as pd
from pathlib import Path
from collections import Counter

LOG_FILE = Path("data/intelion_learning_log.json")

def load_log():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    else:
        print("⚠️ Журнал не найден.")
        return pd.DataFrame()

def analyze_errors(df: pd.DataFrame):
    total = len(df)
    correct = df["correct"].sum()
    accuracy = correct / total * 100 if total > 0 else 0

    wrong_df = df[~df["correct"]]
    surface_errors = wrong_df["surface"].value_counts().to_dict()

    avg_value_errors = wrong_df.apply(
        lambda row: abs(row["prob_player1"] - row["prob_player2"]), axis=1
    ).mean()

    most_common_fail = Counter(wrong_df["predicted_winner"]).most_common(1)

    print(f"📊 Точность модели: {accuracy:.2f}% ({correct}/{total})")
    print(f"🧱 Ошибок по покрытиям: {surface_errors}")
    print(f"📉 Средняя дельта вероятностей при ошибке: {avg_value_errors:.4f}")
    print(f"⚠️ Чаще всего ошибался при прогнозе: {most_common_fail}")

    return {
        "accuracy": accuracy,
        "surface_errors": surface_errors,
        "delta_avg": avg_value_errors,
        "fail_bias": most_common_fail
    }

# Быстрый запуск
if __name__ == "__main__":
    df = load_log()
    if not df.empty:
        analyze_errors(df)
