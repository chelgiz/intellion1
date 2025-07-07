# intellion/reverse_simulator.py

from typing import List, Dict


def simulate_path_to_score(hypothesis: dict, match: dict) -> dict:
    """
    Пытается построить логичный путь к исходу (score), заданному гипотезой.
    Возвращает объяснение и plausibility (оценку правдоподобности).
    """
    winner = hypothesis["winner"]
    score = hypothesis["score"]
    surface = match.get("surface", "Hard")

    explanation = []

    if surface == "Clay":
        explanation.append("Матч на грунте — преимущество у стабильного игрока.")
    elif surface == "Grass":
        explanation.append("Трава усиливает подачу — важен первый мяч.")
    elif surface == "Hard":
        explanation.append("Хард — нейтральное покрытие, решает форма.")

    if score in ["2-0", "3-0"]:
        explanation.append("Чистая победа — физическая и ментальная доминация.")
        plausibility = 0.8
    elif score in ["2-1", "3-1", "3-2"]:
        explanation.append("Соперник дал бой — но фаворит оказался сильнее.")
        plausibility = 0.65
    else:
        explanation.append("Редкий счёт — анализ требует осторожности.")
        plausibility = 0.5

    return {
        "hypothesis": hypothesis,
        "plausibility": plausibility,
        "explanation": explanation
    }


def simulate_from_result(result: dict) -> str:
    """
    Принимает результат матча и реконструирует, как он был достигнут.
    """
    winner = result["winner"]
    score = result["score"]
    surface = result.get("surface", "Unknown")
    explanation = []

    explanation.append(f"📌 Покрытие: {surface}")
    explanation.append(f"🎯 Победитель: {winner} со счётом {score}")

    if surface == "Clay":
        explanation.append("Грунт способствует затяжным розыгрышам.")
    elif surface == "Grass":
        explanation.append("Трава усиливает важность подачи.")
    elif surface == "Hard":
        explanation.append("Хард — универсальное покрытие.")

    if isinstance(score, list):
        score_str = ", ".join(score)
    else:
        score_str = score

    if any("6:0" in s or "6:1" in s for s in score_str.split(",")):
        explanation.append("❗️ Были сет-болты — явное преимущество.")
    if "7:6" in score_str or "6:7" in score_str:
        explanation.append("🎾 Тайбрейки указывают на равную борьбу.")
    if len(score_str.split(",")) >= 4:
        explanation.append("🧱 Долгий матч — фактор выносливости.")

    return "\n".join(explanation)


def generate_set_scores(score: str, winner: str, player1: str, player2: str) -> List[str]:
    """
    Генерирует список сетов (например, ['6:4', '3:6', '6:3']) по гипотетическому счёту.
    winner: '1' или '2' — кто выиграл матч
    """
    sets = []
    set_count = int(score.split("-")[0]) + int(score.split("-")[1])
    w_sets = int(score.split("-")[0]) if winner == "1" else int(score.split("-")[1])
    l_sets = set_count - w_sets

    for i in range(w_sets):
        sets.append("6:4" if winner == "1" else "4:6")
    for i in range(l_sets):
        sets.append("4:6" if winner == "1" else "6:4")

    return sets
