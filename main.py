import datetime

from fastapi import FastAPI, Body, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import load_config
from models.dao import get_test_info, pass_test


# app preparation
app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory='templates')

# database preparation
config = load_config()
db_url = config.db.get_db_url()

engine = create_async_engine(url=db_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# route preparation
app.mount('/static', StaticFiles(directory='static'), 'static')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(name='index.html', context={'request': request})


@app.get("/api/check-test")
async def check_test(test_code: str):
    test = await get_test_info(test_code, async_session_maker=async_session_maker)

    if test is None:
        return {
            'allowed': False,
            'error': 'Test topilmadi'
        }

    if datetime.datetime.now() > test.end_time and False: # for development
        return {
            'allowed': False,
            'error': 'Test Yakunlandi'
        }

    return {
        "allowed": True,
        "minutes": test.test_time,
        "open_questions": test.open_questions,
        "close_questions": test.close_questions,
        "test_name": test.test_name,
        "test_id": test.id
    }


@app.post('/api/submit-test')
async def submit_test(user_answers = Body()):
    user_test_data = {
        'test_id': user_answers['test_id'],
        'username': user_answers['username'],
        'lastname': user_answers['lastname'],
        'city': user_answers['city'],
        'user_id': 123456789,
        'started_at': datetime.datetime.strptime(user_answers['started_at'], '%Y-%m-%d %H:%M:%S.%f'),
        'completed_at': datetime.datetime.strptime(user_answers['completed_at'], '%Y-%m-%d %H:%M:%S.%f'),
        'answers': user_answers['answers']
    }
    await pass_test(user_test_data=user_test_data, async_session_maker=async_session_maker)

