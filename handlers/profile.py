from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.requests.users import get_user_by_tg_id

router = Router()


@router.message(Command("profile"))
async def profile_cmd(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_tg_id(session, message.from_user.id)
    if not user:
        await message.answer("Профиль не найден. Нажми /start")
        return

    await message.answer(
        "👤 Профиль\n\n"
        f"ID: {user.tg_id}\n"
        f"💰 Кредитов: {user.credits}\n"
        f"📊 Всего генераций: {user.total_generations}"
    )
