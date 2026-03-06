from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def post_actions_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔄 Перегенерировать", callback_data="post:regen")
    b.button(text="✏️ Редактировать", callback_data="post:edit")
    b.button(text="➕ Новый пост", callback_data="post:new")
    b.adjust(1)
    return b.as_markup()
