from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from database.requests.users import add_credits
from database.requests.purchases import create_purchase
from keyboards.payments import stars_packages_kb

router = Router()


@router.message(Command("buy"))
async def buy_cmd(message: Message, config: Config) -> None:
    await message.answer(
        "⭐ Доступные пакеты:",
        reply_markup=stars_packages_kb(config.stars_packages)
    )


@router.callback_query(F.data.startswith("buy:"))
async def buy_package(call: CallbackQuery, config: Config, bot, session: AsyncSession) -> None:
    await call.answer()
    
    stars = int(call.data.split(":")[1])
    credits = config.stars_packages.get(stars)
    
    if not credits:
        await call.message.answer("❌ Неверный пакет")
        return

    prices = [LabeledPrice(label=f"{credits} генераций", amount=stars)]
    
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="Покупка генераций",
        description=f"{credits} генераций контента",
        payload=f"credits:{credits}:{stars}",
        provider_token="",
        currency="XTR",
        prices=prices,
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def payment_success(message: Message, session: AsyncSession) -> None:
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    try:
        _, credits_str, stars_str = payload.split(":")
        credits = int(credits_str)
        stars = int(stars_str)
    except (ValueError, IndexError):
        await message.answer("❌ Ошибка обработки платежа")
        return

    await add_credits(session, message.from_user.id, credits)
    
    await create_purchase(
        session=session,
        tg_id=message.from_user.id,
        stars_amount=stars,
        credits_added=credits,
        currency="XTR",
        telegram_charge_id=payment.telegram_payment_charge_id,
        provider_charge_id=payment.provider_payment_charge_id,
    )

    await message.answer(f"✅ Оплачено! +{credits} генераций")
