import datetime
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from redis.asyncio import Redis

from app.config import load_config, PATH
from app.models.dao import get_test_info, pass_test
from app.pydantic_models import SubmitTest
from app.tg_bot.bot import bot, dp, bot_preparation, set_all_commands


# app preparation
@asynccontextmanager
async def lifespan(app: FastAPI):
    templates = Jinja2Templates(directory=PATH / 'app/templates')
    app.templates = templates
    app.mount('/app/static', StaticFiles(directory='app/static'), name='static')

    # database preparation
    config = load_config(PATH / '.env')
    db_url = config.get_db_url()

    engine = create_async_engine(url=db_url)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    app.async_session_maker = async_session_maker

    # redis preparation
    redis = await Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    app.redis = redis

    # tg bot preparation
    bot.async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    await bot_preparation()

    yield

    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)

origins = ['*']
app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root(request: Request):
    return app.templates.TemplateResponse(name='index.html', context={'request': request})


@app.get("/api/check-test")
async def check_test(test_code: str):
    test = await get_test_info(test_code, async_session_maker=app.async_session_maker, redis=app.redis)

    if not test:
        return {
            'allowed': False,
            'error': 'Test topilmadi'
        }

    end_time = datetime.datetime.strptime(test['end_time'], '%Y-%m-%d %H:%M:%S.%f')

    if datetime.datetime.now() > end_time and False: # for development
        return {
            'allowed': False,
            'error': 'Test Yakunlandi'
        }

    test['allowed'] = True

    return test


@app.post('/api/submit-test')
async def submit_test(user_answers: SubmitTest):
    user_answers.started_at = datetime.datetime.strptime(user_answers.started_at, '%Y-%m-%d %H:%M:%S.%f')
    user_answers.completed_at = datetime.datetime.strptime(user_answers.completed_at, '%Y-%m-%d %H:%M:%S.%f')
    await pass_test(user_test_data=user_answers, async_session_maker=app.async_session_maker)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    # Получаем данные обновления из запроса
    update_data = await request.json()

    # Преобразуем данные в объект Update
    update = Update(**update_data)

    # Передаем обновление в диспетчер
    await dp.feed_update(bot, update)

