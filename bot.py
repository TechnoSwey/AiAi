import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from database.base import Base
from database.session import create_engine_and_sessionmaker
from middlewares.db import DbSessionMiddleware
from services.ai_service import AiService
from handlers import start, profile, post_creation, payments, admin


async def on_startup(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


async def main():
    setup_logging()
    config = load_config()

    engine, sessionmaker = create_engine_and_sessionmaker(config)
    await on_startup(engine)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    ai = AiService(api_url=config.ai_api_url, api_key=config.ai_api_key)

    dp.update.middleware(DbSessionMiddleware(sessionmaker))

    dp["config"] = config
    dp["ai"] = ai

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(post_creation.router)
    dp.include_router(payments.router)
    dp.include_router(admin.router)

    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
