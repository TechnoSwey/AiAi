from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.purchase import Purchase


async def create_purchase(
    session: AsyncSession,
    tg_id: int,
    stars_amount: int,
    credits_added: int,
    currency: str,
    telegram_charge_id: str,
    provider_charge_id: str,
) -> Purchase:
    p = Purchase(
        tg_id=tg_id,
        stars_amount=stars_amount,
        credits_added=credits_added,
        currency=currency,
        telegram_charge_id=telegram_charge_id,
        provider_charge_id=provider_charge_id,
    )
    session.add(p)
    await session.commit()
    await session.refresh(p)
    return p


async def get_purchases_count(session: AsyncSession) -> int:
    res = await session.execute(select(func.count(Purchase.id)))
    return int(res.scalar() or 0)


async def get_purchases_sum_stars(session: AsyncSession) -> int:
    res = await session.execute(select(func.coalesce(func.sum(Purchase.stars_amount), 0)))
    return int(res.scalar() or 0)
