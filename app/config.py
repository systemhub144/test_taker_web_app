from environs import Env
from pydantic_settings import BaseSettings
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
PATH = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int

    BOT_TOKEN: str
    BASE_URL: str

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    def get_webhook_url(self) -> str:
        return f"{self.BASE_URL}/webhook"


def load_config(path: Path) -> Settings:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info('Get config')

    env = Env()
    env.read_env(path)

    config = Settings(
        DB_HOST=env.str('DB_HOST'),
        DB_USER=env.str('DB_USER'),
        DB_PASSWORD=env.str('DB_PASSWORD'),
        DB_NAME=env.str('DB_NAME'),
        DB_PORT=env.int('DB_PORT'),
        REDIS_HOST=env.str('REDIS_HOST'),
        REDIS_PORT=env.int('REDIS_PORT'),
        BOT_TOKEN=env.str('BOT_TOKEN'),
        BASE_URL=env.str('BASE_URL'),
    )

    config.get_db_url()

    return config