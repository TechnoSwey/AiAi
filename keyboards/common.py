from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Новый пост"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="⭐ Купить"), KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )
