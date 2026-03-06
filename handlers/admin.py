from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from database.models.user import User
from database.requests.users import add_credits, set_credits
from database.requests.purchases import get_purchases_count, get_purchases_sum_stars
from database.requests.posts import get_posts_count
from keyboards.admin import admin_menu_kb
from states.admin import AdminBroadcast, AdminCredits

router = Router()


def _is_admin(user_id: int, config: Config) -> bool:
    return user_id in config.admin_ids


@router.message(Command("admin"))
async def admin_cmd(message: Message, config: Config) -> None:
    if not _is_admin(message.from_user.id, config):
        return
    await message.answer("🔧 Админ-панель:", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(call: CallbackQuery, session: AsyncSession, config: Config) -> None:
    if not _is_admin(call.from_user.id, config):
        await call.answer()
        return
    await call.answer()

    users_count = await session.scalar(select(func.count(User.id)))
    posts_count = await get_posts_count(session)
    purchases_count = await get_purchases_count(session)
    stars_sum = await get_purchases_sum_stars(session)

    await call.message.answer(
        "📊 Статистика:\n\n"
        f"👥 Пользователей: {users_count or 0}\n"
        f"📝 Постов: {posts_count}\n"
        f"💳 Покупок: {purchases_count}\n"
        f"⭐ Выручка: {stars_sum}"
    )


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext, config: Config) -> None:
    if not _is_admin(call.from_user.id, config):
        await call.answer()
        return
    await call.answer()
    await state.set_state(AdminBroadcast.text)
    await call.message.answer("📢 Введите текст для рассылки:")


@router.message(AdminBroadcast.text)
async def admin_broadcast_send(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    config: Config
) -> None:
    if not _is_admin(message.from_user.id, config):
        await state.clear()
        return

    text = (message.text or "").strip()
    if not text:
        await message.answer("❌ Пустой текст")
        return

    users = await session.execute(select(User.tg_id))
    ids = [row[0] for row in users.all()]

    ok = 0
    fail = 0
    for tg_id in ids:
        try:
            await bot.send_message(tg_id, text)
            ok += 1
        except Exception:
            fail += 1

    await state.clear()
    await message.answer(f"✅ Рассылка завершена\nУспешно: {ok}\nОшибок: {fail}")


@router.callback_query(F.data.in_({"admin:add_credits", "admin:set_credits"}))
async def admin_credits_start(call: CallbackQuery, state: FSMContext, config: Config) -> None:
    if not _is_admin(call.from_user.id, config):
        await call.answer()
        return
    await call.answer()
    mode = call.data.split(":")[1]
    await state.update_data(mode=mode)
    await state.set_state(AdminCredits.target_tg_id)
    await call.message.answer("👤 Введите TG ID пользователя:")


@router.message(AdminCredits.target_tg_id)
async def admin_credits_target(message: Message, state: FSMContext, config: Config) -> None:
    if not _is_admin(message.from_user.id, config):
        await state.clear()
        return
    try:
        tg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Нужно число")
        return
    await state.update_data(target_tg_id=tg_id)
    await state.set_state(AdminCredits.amount)
    await message.answer("💰 Введите количество кредитов:")


@router.message(AdminCredits.amount)
async def admin_credits_apply(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    config: Config
) -> None:
    if not _is_admin(message.from_user.id, config):
        await state.clear()
        return

    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Нужно число")
        return

    data = await state.get_data()
    target_tg_id = data["target_tg_id"]
    mode = data["mode"]

    if mode == "add_credits":
        await add_credits(session, target_tg_id, amount)
        await message.answer(f"✅ Добавлено {amount} кредитов пользователю {target_tg_id}")
    else:
        await set_credits(session, target_tg_id, amount)
        await message.answer(f"✅ Установлено {amount} кредитов пользователю {target_tg_id}")

    await state.clear()
