# intellion/fractal_pattern_scaner.py

from typing import List, Dict

def scan_fractal_pattern(current_match: Dict, historical_data: List[Dict]) -> Dict:
    """
    Ищет похожие матчи из истории с учетом покрытия и близких коэффициентов.

    current_match: {
        'player1': 'A. Zverev',
        'player2': 'J. Sinner',
        'surface': 'Clay',
        'odds_player1': 1.85,
        'odds_player2': 2.10
    }

    historical_data: список словарей с аналогичной структурой + результатом
    """

    matches_found = []
    for past in historical_data:
        same_surface = current_match["surface"] == past["surface"]
        odds_diff = abs(current_match["odds_player1"] - past["odds_player1"]) < 0.15
        inverse_odds = abs(current_match["odds_player1"] - past["odds_player2"]) < 0.15 and \
                       abs(current_match["odds_player2"] - past["odds_player1"]) < 0.15

        if same_surface and (odds_diff or inverse_odds):
            matches_found.append({
                "match": f"{past['player1']} vs {past['player2']}",
                "result": past.get("result", "?"),
                "odds": (past["odds_player1"], past["odds_player2"]),
                "surface": past["surface"]
            })

    return {
        "current_match": f"{current_match['player1']} vs {current_match['player2']}",
        "surface": current_match['surface'],
        "found_similar_patterns": matches_found,
        "pattern_strength": round(len(matches_found) / max(len(historical_data), 1), 2)
    }
