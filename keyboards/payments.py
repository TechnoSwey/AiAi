from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def stars_packages_kb(packages: dict[int, int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for stars, credits in sorted(packages.items()):
        b.button(text=f"{stars}⭐ → {credits} генераций", callback_data=f"buy:{stars}")
    b.adjust(1)
    return b.as_markup()
