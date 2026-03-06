from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import Config


def create_engine_and_sessionmaker(cfg: Config):
    engine = create_async_engine(cfg.database_url, echo=False, future=True)
    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, sessionmaker
