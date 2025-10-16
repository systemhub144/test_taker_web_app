from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dao.dao import TestDAO, UserDAO, TestCreatorDAO
from app.models.database import connection
from app.pydantic_models.test import SubmitTest


@connection
async def pass_test(user_test_data: SubmitTest, session: AsyncSession):
    user_attempt = await UserDAO.pass_test(session=session, user_test_data=user_test_data)
    return user_attempt


@connection
async def add_full_test(test_data: dict, session: AsyncSession) -> int:
    new_test = await TestDAO.add_test_with_answers(session=session, test_data=test_data)
    return new_test.id


@connection
async def add_new_admin(user_id: int, session: AsyncSession):
    await TestCreatorDAO.new_admin(session=session, user_id=user_id)
