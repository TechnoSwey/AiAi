from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📊 Статистика", callback_data="admin:stats")
    b.button(text="📢 Рассылка", callback_data="admin:broadcast")
    b.button(text="➕ Добавить кредиты", callback_data="admin:add_credits")
    b.button(text="⚙️ Установить кредиты", callback_data="admin:set_credits")
    b.adjust(1)
    return b.as_markup()
