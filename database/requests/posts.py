from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.post import PostHistory


async def save_post_history(
    session: AsyncSession,
    tg_id: int,
    topic: str,
    audience: str,
    tone: str,
    platform: str,
    requirements: str,
    prompt: str,
    result_text: str,
) -> PostHistory:
    row = PostHistory(
        tg_id=tg_id,
        topic=topic,
        audience=audience,
        tone=tone,
        platform=platform,
        requirements=requirements,
        prompt=prompt,
        result_text=result_text,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def get_posts_count(session: AsyncSession) -> int:
    res = await session.execute(select(func.count(PostHistory.id)))
    return int(res.scalar() or 0)
