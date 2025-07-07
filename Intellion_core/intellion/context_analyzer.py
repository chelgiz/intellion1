from news_fetcher import get_news
from got_analyzer import analyze_player_state
from emotion_predictor import analyze_emotion_signals
from resonance_analyzer import diagnose_resonance


def get_context_data(player1: str, player2: str, surface: str) -> dict:
    """
    Собирает полный контекст по игрокам: новости, эмоциональное состояние, резонанс.
    """
    p1_news = get_news(player1)
    p2_news = get_news(player2)

    p1_state = analyze_player_state(player1, surface, p1_news)
    p2_state = analyze_player_state(player2, surface, p2_news)

    p1_emotion = analyze_emotion_signals(player1, p1_news)
    p2_emotion = analyze_emotion_signals(player2, p2_news)

    p1_resonance = diagnose_resonance(player1, p1_news)
    p2_resonance = diagnose_resonance(player2, p2_news)

    return {
        "player1": {
            "state": p1_state,
            "emotion": p1_emotion,
            "resonance": p1_resonance,
        },
        "player2": {
            "state": p2_state,
            "emotion": p2_emotion,
            "resonance": p2_resonance,
        }
    }
