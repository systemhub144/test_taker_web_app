from models.dao.dao import TestDAO, UserDAO
from models.database import connection

from sqlalchemy.ext.asyncio import AsyncSession


@connection
async def pass_test(user_test_data: dict, session: AsyncSession):
    user_attempt = await UserDAO.pass_test(session=session, user_test_data=user_test_data)
    return user_attempt


@connection
async def add_full_test(test_data: dict, session: AsyncSession):
    new_test = await TestDAO.add_test_with_answers(session=session, test_data=test_data)
    return new_test.id
