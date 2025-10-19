import json

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dao.dao import TestDAO
from app.models.database import connection


@connection
async def stop_testing(test_id: str, session: AsyncSession, redis: Redis) -> bool:
    redis_test = await redis.get(test_id)
    if not redis_test is None:
        redis_test = json.loads(redis_test)
        redis_test['is_ended'] = True

        await redis.set(test_id, json.dumps(redis_test))

    return await TestDAO.stop_test(test_id=int(test_id), session=session)
