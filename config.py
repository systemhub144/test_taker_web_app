import os

from dataclasses import dataclass
from environs import Env
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


class DBSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # DATABASE_SQLITE = 'sqlite+aiosqlite:///data/db.sqlite3'
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


class RedisSettings(BaseSettings):
    host: str
    port: int


@dataclass
class Config:
    db: DBSettings
    redis: RedisSettings


def load_config() -> Config:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info('Get config')

    env = Env()
    env.read_env('.env')

    config = Config(
        db=DBSettings(
            DB_HOST=env.str('DB_HOST'),
            DB_USER=env.str('DB_USER'),
            DB_PASSWORD=env.str('DB_PASSWORD'),
            DB_NAME=env.str('DB_NAME'),
            DB_PORT=env.int('DB_PORT'),
        ),
        redis=RedisSettings(
            host=env.str('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
        )
    )

    config.db.get_db_url()

    return config