import datetime
import json

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from models.dao.dao import TestDAO
from models.database import connection


@connection
async def get_test_info(test_id: str, session: AsyncSession, redis: Redis) -> dict:
    test_data = await redis.get(test_id)
    if test_data is None:
        test = await TestDAO().get_test_info_by_name(test_id=test_id, session=session)
        test_new_data = {
            "minutes": test.test_time,
            "open_questions": test.open_questions,
            "close_questions": test.close_questions,
            "test_name": test.test_name,
            "test_id": test.id,
            "start_time": str(test.start_time),
            "end_time": str(test.end_time),
        }

        await redis.set(test_id, json.dumps(test_new_data))

        return test_new_data

    return json.loads(test_data)
