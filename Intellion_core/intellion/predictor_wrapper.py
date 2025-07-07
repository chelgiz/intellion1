# intellion/predictor_wrapper.py

import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path("models/catboost_model.pkl")
FEATURES = [
    "surface_type",
    "odds_ratio",
    "sets_total",
    "straight_sets_win",
    "bo5_match",
    "long_match_flag"
]

CATEGORICAL = ["surface_type"]

def preprocess_match(match: dict) -> pd.DataFrame:
    """
    Подготавливает данные одного матча в формате, подходящем для модели.
    """
    data = {
        "player1": match["player1"],
        "player2": match["player2"],
        "surface_type": match.get("surface_type", "Hard"),
        "odds_ratio": round(min(match["odds_player1"], match["odds_player2"]) /
                            max(match["odds_player1"], match["odds_player2"]), 4),
        "sets_total": 0,  # фиктивно
        "straight_sets_win": 0,  # фиктивно
        "bo5_match": int(match.get("bo5_match", False)),
        "long_match_flag": 0  # фиктивно
    }
    return pd.DataFrame([data])

def predict_match(match: dict) -> dict:
    """
    Возвращает предсказание модели:
    - вероятность победы первого игрока
    - вероятность победы второго игрока
    """
    model = joblib.load(MODEL_PATH)
    df = preprocess_match(match)

    prob = model.predict_proba(df)[0]  # [P(class=0), P(class=1)]

    return {
        "prob_player1": prob[1],  # class 1 — победа первого
        "prob_player2": prob[0],  # class 0 — победа второго
        "features": df.to_dict(orient="records")[0]
    }
