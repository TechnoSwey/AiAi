from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    return res.scalar_one_or_none()


async def create_user_if_not_exists(
    session: AsyncSession,
    tg_id: int,
    username: str | None,
    full_name: str | None,
    initial_credits: int,
) -> tuple[User, bool]:
    user = await get_user_by_tg_id(session, tg_id)
    if user:
        return user, False
    user = User(
        tg_id=tg_id,
        username=username,
        full_name=full_name,
        credits=initial_credits
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def add_credits(session: AsyncSession, tg_id: int, amount: int) -> None:
    await session.execute(
        update(User)
        .where(User.tg_id == tg_id)
        .values(credits=User.credits + amount)
    )
    await session.commit()


async def set_credits(session: AsyncSession, tg_id: int, amount: int) -> None:
    await session.execute(
        update(User)
        .where(User.tg_id == tg_id)
        .values(credits=amount)
    )
    await session.commit()


async def try_consume_credit(session: AsyncSession, tg_id: int) -> bool:
    user = await get_user_by_tg_id(session, tg_id)
    if not user or user.credits <= 0:
        return False

    await session.execute(
        update(User)
        .where(User.tg_id == tg_id)
        .where(User.credits > 0)
        .values(
            credits=User.credits - 1,
            total_generations=User.total_generations + 1
        )
    )
    await session.commit()
    return True
