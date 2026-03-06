import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise RuntimeError(f"Missing env var: {name}")
    return v


def _parse_admin_ids(raw: str) -> List[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class Config:
    bot_token: str
    ai_api_key: str
    ai_api_url: str
    database_url: str
    admin_ids: List[int]
    free_generations_on_start: int = 3
    stars_packages: dict[int, int] = None

    def __post_init__(self):
        object.__setattr__(self, 'stars_packages', {50: 10, 100: 25, 200: 60})


def load_config() -> Config:
    return Config(
        bot_token=_get_env("BOT_TOKEN"),
        ai_api_key=_get_env("AI_API_KEY"),
        ai_api_url=_get_env("AI_API_URL"),
        database_url=_get_env("DATABASE_URL"),
        admin_ids=_parse_admin_ids(_get_env("ADMIN_IDS", "")),
    )
