from sqlalchemy.ext.asyncio import AsyncSession

from models.dao.dao import TestDAO
from models.database import connection


@connection
async def get_test_info(test_id: str, session: AsyncSession):
    test = await TestDAO().get_test_info_by_name(test_id=test_id, session=session)
    return test

