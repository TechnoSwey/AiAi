from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from database.requests.users import create_user_if_not_exists
from keyboards.common import main_menu

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message, session: AsyncSession, config: Config) -> None:
    user, created = await create_user_if_not_exists(
        session=session,
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        initial_credits=config.free_generations_on_start,
    )

    if created:
        text = (
            "👋 Привет! Я ИИ-помощник контент-менеджера.\n\n"
            f"🎁 У тебя {user.credits} бесплатных генераций.\n"
            "📝 /new_post — создать пост"
        )
    else:
        text = "👋 С возвращением!\n📝 /new_post — создать пост\n👤 /profile — профиль\n⭐ /buy — пополнить"

    await message.answer(text, reply_markup=main_menu())


@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer(
        "📌 Команды:\n"
        "/new_post — создать пост (1 кредит)\n"
        "/profile — баланс и статистика\n"
        "/buy — купить генерации за Telegram Stars\n"
        "/help — это меню"
    )
