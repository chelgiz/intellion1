# intellion/feature_engeneering.py

import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/training_data.csv")
PROCESSED_PATH = Path("data/processed_data.csv")

def load_data():
    return pd.read_csv(RAW_DATA_PATH)

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Целевая переменная: победа первого игрока
    df["winner_encoded"] = (df["winner"] == df["player1"]).astype(int)

    # Количество сетов в матче
    def sets_count(score: str) -> int:
        try:
            return len(str(score).split(","))
        except:
            return 0

    # Победа всухую (2:0 или 3:0)
    def straight_sets_win(score: str) -> int:
        try:
            sets = [s.strip() for s in str(score).split(",")]
            p1_sets, p2_sets = 0, 0
            for s in sets:
                g1, g2 = map(int, s.split(":"))
                if g1 > g2:
                    p1_sets += 1
                else:
                    p2_sets += 1
            # Победа всухую возможна при 2:0 или 3:0
            if (p1_sets == 2 or p1_sets == 3) and p2_sets == 0:
                return 1
            if (p2_sets == 2 or p2_sets == 3) and p1_sets == 0:
                return 1
            return 0
        except:
            return 0

    # Разница в кэфах
    def odds_ratio(row):
        try:
            o1 = float(row.get("odds_player1", 0))
            o2 = float(row.get("odds_player2", 0))
            if o1 > 0 and o2 > 0:
                return round(min(o1, o2) / max(o1, o2), 4)
            else:
                return 0
        except:
            return 0

    df["sets_total"] = df["score"].apply(sets_count)
    df["straight_sets_win"] = df["score"].apply(straight_sets_win)
    df["odds_ratio"] = df.apply(odds_ratio, axis=1)

    # Категориальные признаки
    df["surface_type"] = df["surface"].astype(str).fillna("Unknown")

    # Дополнительные бинарные признаки
    df["bo5_match"] = (df["sets_total"] >= 4).astype(int)       # матч до 3 побед
    df["long_match_flag"] = (df["sets_total"] >= 5).astype(int) # выматывающий бой

    # Итоговый набор признаков
    df = df[[
        "player1", "player2", "surface_type", "odds_ratio",
        "sets_total", "straight_sets_win", "bo5_match",
        "long_match_flag", "winner_encoded"
    ]]

    return df

def save_features(df: pd.DataFrame):
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"✅ Фичи сохранены: {len(df)} записей → {PROCESSED_PATH}")

if __name__ == "__main__":
    raw_df = load_data()
    features_df = extract_features(raw_df)
    save_features(features_df)
