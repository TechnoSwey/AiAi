def build_prompt(
    topic: str,
    audience: str,
    tone: str,
    platform: str,
    requirements: str,
) -> str:
    return (
        "Ты — ИИ-помощник контент-менеджера. Сгенерируй готовый пост.\n\n"
        f"ТЕМА: {topic}\n"
        f"ЦЕЛЕВАЯ АУДИТОРИЯ: {audience}\n"
        f"ТОН: {tone}\n"
        f"ПЛАТФОРМА: {platform}\n"
        f"ДОП. ТРЕБОВАНИЯ: {requirements}\n\n"
        "Требования к ответу:\n"
        "- Дай только текст поста (без пояснений).\n"
        "- Структурируй, если уместно.\n"
        "- Без воды."
    )
