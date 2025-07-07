# intellion/resonance_analyzer.py

def diagnose_resonance(player1_news: list[str], player2_news: list[str]) -> dict:
    """
    Эвристика: если количество новостей про одного игрока сильно выше — это потенциальный инфошум.
    """
    p1_count = len(player1_news)
    p2_count = len(player2_news)

    diff = abs(p1_count - p2_count)
    dominant_player = None

    if diff >= 3:
        dominant_player = "Player 1" if p1_count > p2_count else "Player 2"

    return {
        "player1_mentions": p1_count,
        "player2_mentions": p2_count,
        "dominant_info_flow": dominant_player,
        "resonance_score": diff / max(p1_count + p2_count, 1)
    }
