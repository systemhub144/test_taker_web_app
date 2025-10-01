import datetime
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo
import pytz

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from redis.asyncio import Redis

from app.config import load_config, PATH
from app.models.dao import get_test_info, pass_test, add_full_test
from app.pydantic_models import SubmitTest, CreateTest
from app.tg_bot.bot import bot, dp, bot_preparation


# app preparation
@asynccontextmanager
async def lifespan(app: FastAPI):
    templates = Jinja2Templates(directory=PATH / 'app/templates')
    app.templates = templates
    app.mount('/app/static', StaticFiles(directory='app/static'), name='static')

    # database preparation
    config = load_config(PATH / '.env')
    db_url = config.get_db_url()
    app.config = config

    engine = create_async_engine(url=db_url)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, poolclass=NullPool)
    app.async_session_maker = async_session_maker

    # redis preparation
    redis = await Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    app.redis = redis

    # tg bot preparation
    bot.async_session_maker = async_sessionmaker(engine, expire_on_commit=False, poolclass=NullPool)

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
    return app.templates.TemplateResponse(name='pass_test.html', context={'request': request})


@app.get("/api/check-test")
async def check_test(test_code: str):
    test = await get_test_info(test_code, async_session_maker=app.async_session_maker, redis=app.redis)

    if not test:
        return {
            'allowed': False,
            'error': 'Test topilmadi'
        }
    utc = pytz.UTC

    end_time = datetime.datetime.strptime(test['end_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)
    start_time = datetime.datetime.strptime(test['start_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)

    tz_gmt_plus_5 = ZoneInfo("Etc/GMT-5")
    current_time = datetime.datetime.now(tz_gmt_plus_5)

    if current_time > end_time:
        return {
            'allowed': False,
            'error': 'Test Yakunlandi'
        }
    if start_time > current_time:
        return {
            'allowed': False,
            'error': 'Test Boshlanmagan'
        }

    test['allowed'] = True

    return test


@app.post('/api/submit-test')
async def submit_test(user_answers: SubmitTest):
    user_answers.started_at = datetime.datetime.strptime(user_answers.started_at, '%Y-%m-%d %H:%M:%S.%f')
    user_answers.completed_at = datetime.datetime.strptime(user_answers.completed_at, '%Y-%m-%d %H:%M:%S.%f')
    user_results = await pass_test(user_test_data=user_answers, async_session_maker=app.async_session_maker)

    message = (f'testning natijalari\n'
               f'Ism: {user_results['username']}\n'
               f'Familiyasi: {user_results['lastname']}\n'
               f'Viloyat: {user_results['city']}\n'
               f'user id: {user_results['user_id']}\n'
               f'Togri javoblar: {user_results['correct_answers']}\n'
               f'Hato javoblari: {user_results['wrong_answers']}\n'
               f'Balli: {user_results['score']}\n')

    test_info = await get_test_info(test_id=user_results['test_id'], async_session_maker=app.async_session_maker, by_id=True)

    await bot.send_message(text=message, chat_id=test_info['admin_id'])


@app.post("/webhook")
async def webhook(request: Request) -> None:
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)


@app.get("/create/test")
async def root(request: Request):
    return app.templates.TemplateResponse(name='create_test.html', context={'request': request})


@app.get('/api/create/test/check')
async def check_test_name(test_name: str):
    test = await get_test_info(test_name, async_session_maker=app.async_session_maker, redis=app.redis)
    if test is None:
        return {
            'allowed': True
        }
    return {
        'allowed': False,
        'error': 'Test yaratilib bolingan'
    }


@app.post('/api/create/test')
async def create_test(test_data: CreateTest):
    try:
        test_data.start_time = datetime.datetime.strptime(test_data.start_time, '%Y-%m-%d %H:%M:%S.%f')
        test_data.end_time = datetime.datetime.strptime(test_data.end_time, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as e:
        raise {
            'created': False,
            'error': 'The format of time is incorrect',
        }

    await add_full_test(test_data=test_data, async_session_maker=app.async_session_maker)

    await bot.send_message(chat_id=test_data.user_id, text=f'Test yaratilindi\n'
                                                           f'codi: {test_data.test_name}\n'
                                                           f'test vaqti: {test_data.test_time} minut\n'
                                                           f'ishlash vaqti:\n'
                                                           f'{test_data.start_time} dan\n'
                                                           f'{test_data.end_time} gacha\n')

    return {
        'created': True,
        'errors': None
    }
