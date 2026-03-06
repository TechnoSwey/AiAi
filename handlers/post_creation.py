from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.requests.users import try_consume_credit, get_user_by_tg_id, add_credits
from database.requests.posts import save_post_history
from keyboards.post import post_actions_kb
from services.ai_service import AiService, AiServiceError
from services.prompt_builder import build_prompt
from states.post_creation import PostCreation

router = Router()


def _fmt_summary(data: dict) -> str:
    return (
        "Проверьте вводные:\n\n"
        f"📌 Тема: {data.get('topic')}\n"
        f"👥 ЦА: {data.get('audience')}\n"
        f"🎭 Тон: {data.get('tone')}\n"
        f"📱 Платформа: {data.get('platform')}\n"
        f"📋 Требования: {data.get('requirements')}\n\n"
        "✅ Напишите 'да' для генерации\n"
        "✏️ Или отправьте исправление для любого пункта"
    )


@router.message(Command("new_post"))
async def new_post_cmd(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PostCreation.topic)
    await message.answer("📝 Введите тему поста:")


@router.message(PostCreation.topic)
async def topic_step(message: Message, state: FSMContext) -> None:
    await state.update_data(topic=message.text.strip())
    await state.set_state(PostCreation.audience)
    await message.answer("👥 Целевая аудитория:")


@router.message(PostCreation.audience)
async def audience_step(message: Message, state: FSMContext) -> None:
    await state.update_data(audience=message.text.strip())
    await state.set_state(PostCreation.tone)
    await message.answer("🎭 Тон (дружелюбный/деловой/дерзкий/мотивирующий):")


@router.message(PostCreation.tone)
async def tone_step(message: Message, state: FSMContext) -> None:
    await state.update_data(tone=message.text.strip())
    await state.set_state(PostCreation.platform)
    await message.answer("📱 Платформа (Telegram/Instagram/VK):")


@router.message(PostCreation.platform)
async def platform_step(message: Message, state: FSMContext) -> None:
    await state.update_data(platform=message.text.strip())
    await state.set_state(PostCreation.requirements)
    await message.answer("📋 Дополнительные требования (хэштеги, CTA, структура):")


@router.message(PostCreation.requirements)
async def requirements_step(message: Message, state: FSMContext) -> None:
    await state.update_data(requirements=message.text.strip())
    data = await state.get_data()
    await state.set_state(PostCreation.confirm)
    await message.answer(_fmt_summary(data))


@router.message(PostCreation.confirm)
async def confirm_step(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    ai: AiService,
) -> None:
    text = (message.text or "").strip().lower()
    
    if text != "да":
        # Просто обновляем последнее поле
        await state.update_data(requirements=message.text.strip())
        data = await state.get_data()
        await message.answer(_fmt_summary(data))
        return

    tg_id = message.from_user.id
    ok = await try_consume_credit(session, tg_id)
    if not ok:
        await message.answer("❌ Недостаточно кредитов. Используйте /buy для пополнения")
        await state.clear()
        return

    data = await state.get_data()
    prompt = build_prompt(
        topic=data["topic"],
        audience=data["audience"],
        tone=data["tone"],
        platform=data["platform"],
        requirements=data["requirements"],
    )

    await message.answer("⏳ Генерирую пост...")

    try:
        result = await ai.generate(prompt)
    except AiServiceError as e:
        await add_credits(session, tg_id, 1)
        await message.answer(f"❌ Ошибка генерации: {e}\nКредит возвращён")
        await state.clear()
        return

    await save_post_history(
        session=session,
        tg_id=tg_id,
        topic=data["topic"],
        audience=data["audience"],
        tone=data["tone"],
        platform=data["platform"],
        requirements=data["requirements"],
        prompt=prompt,
        result_text=result,
    )

    await state.update_data(last_prompt=prompt, last_result=result)
    await message.answer(f"✅ Готово:\n\n{result}", reply_markup=post_actions_kb())


@router.callback_query(F.data == "post:regen")
async def regen_post(
    call: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    ai: AiService,
) -> None:
    await call.answer()

    data = await state.get_data()
    prompt = data.get("last_prompt")
    if not prompt:
        await call.message.answer("❌ Нет данных. Начните с /new_post")
        return

    ok = await try_consume_credit(session, call.from_user.id)
    if not ok:
        await call.message.answer("❌ Недостаточно кредитов. /buy")
        return

    await call.message.answer("⏳ Перегенерирую...")

    try:
        result = await ai.generate(prompt)
    except AiServiceError as e:
        await add_credits(session, call.from_user.id, 1)
        await call.message.answer(f"❌ Ошибка: {e}\nКредит возвращён")
        return

    await state.update_data(last_result=result)
    await call.message.answer(f"✅ Новый вариант:\n\n{result}", reply_markup=post_actions_kb())


@router.callback_query(F.data == "post:edit")
async def edit_post(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    data = await state.get_data()
    if not data.get("last_result"):
        await call.message.answer("❌ Нечего редактировать. Сначала создайте пост")
        return
    await state.set_state(PostCreation.editing)
    await call.message.answer("✏️ Отправьте отредактированный текст:")


@router.message(PostCreation.editing)
async def save_edited(message: Message, state: FSMContext, session: AsyncSession) -> None:
    edited = (message.text or "").strip()
    if not edited:
        await message.answer("❌ Пустой текст. Отправьте ещё раз")
        return

    data = await state.get_data()
    prompt = data.get("last_prompt", "")

    await save_post_history(
        session=session,
        tg_id=message.from_user.id,
        topic=data.get("topic", ""),
        audience=data.get("audience", ""),
        tone=data.get("tone", ""),
        platform=data.get("platform", ""),
        requirements=data.get("requirements", ""),
        prompt=prompt,
        result_text=edited,
    )

    await state.update_data(last_result=edited)
    await state.set_state(None)
    await message.answer("✅ Изменения сохранены в истории", reply_markup=post_actions_kb())


@router.callback_query(F.data == "post:new")
async def post_new(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await call.message.answer("📝 Введите тему нового поста:")
    await state.set_state(PostCreation.topic)
