import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.dao.base import BaseDAO
from app.models.models import Test, User, TestAttempt, Answer, UserAnswer
from app.pydantic_models import SubmitTest


class TestDAO(BaseDAO):
    model = Test

    @classmethod
    async def add_test_with_answers(cls, session: AsyncSession, test_data: dict) -> Test:
        test = cls.model(
            test_name=test_data['test_name'],
            open_questions=test_data['open_questions'],
            close_questions=test_data['close_questions'],
            test_time=test_data['test_time'],
            start_time=test_data['start_time'],
            end_time=test_data['end_time'],
            is_ended=test_data['is_ended'],
        )

        session.add(test)
        await session.flush()

        for answer_data in test_data['answers']:
            answer = Answer(
                question_number=answer_data['question_number'],
                question_type=answer_data['question_type'],
                correct_answer=answer_data['correct_answer'],
                test_id=test.id,
                score=answer_data['score'],
            )
            session.add(answer)

        await session.commit()

        return test

    @classmethod
    async def get_test_info_by_name(cls, session: AsyncSession, test_id: str) -> Test:
        stmt = select(Test).where(Test.test_name == test_id)
        return (await session.execute(stmt)).scalars().first()


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def pass_test(cls, session: AsyncSession, user_test_data: SubmitTest) -> bool:
        stmt = select(Answer).where(Answer.test_id == user_test_data.test_id)
        answers = (await session.execute(stmt)).scalars().all()

        user = cls.model(
            username=user_test_data.username,
            city=user_test_data.city,
            user_id=user_test_data.user_id,
            lastname=user_test_data.lastname,
        )

        session.add(user)
        await session.flush()

        test_results = {
            'correct_answers': 0,
            'wrong_answers': 0,
            'score': 0
        }

        for answer in answers:
            user_answer = user_test_data.answers[answer.question_number - 1]
            if answer.correct_answer == user_answer:
                test_results['correct_answers'] += 1
                test_results['score'] += answer.score
            else:
                test_results['wrong_answers'] += 1

        test_attempt = TestAttempt(
            test_id=user_test_data.test_id,
            tg_user_id=user_test_data.user_id,
            user_id=user.id,
            score=test_results['score'],
            correct_answers=test_results['correct_answers'],
            wrong_answers=test_results['wrong_answers'],
            started_at=datetime.datetime.now(),
            completed_at=datetime.datetime.now(),
        )
        session.add(test_attempt)
        await session.flush()

        for answer in answers:
            user_answer_data = user_test_data.answers[answer.question_number - 1]

            user_answer = UserAnswer(
                attempt_id=test_attempt.id,
                answer_id=answer.id,
                user_answer=user_answer_data,
                is_correct=(user_answer_data == answer.correct_answer),
                test_id=user_test_data.test_id
            )
            session.add(user_answer)
            await session.flush()

        await session.commit()

        return True


class TestAttemptDAO(BaseDAO):
    model = TestAttempt

    @classmethod
    async def get_all_results(cls, user_id: int, session: AsyncSession) -> dict:
        results = {}

        stmt = select(TestAttempt).where(TestAttempt.tg_user_id == user_id)
        user_attempts = (await session.execute(stmt)).scalars().all()

        for user_attempt in user_attempts:
            stmt = select(Test).where(Test.id == user_attempt.test_id)
            test = (await session.execute(stmt)).scalars().first()
            results[test.test_name] = user_attempt

        return results

    @classmethod
    async def get_user_answers(cls, user_attempt: int, session: AsyncSession) -> Sequence[UserAnswer]:
        stmt = select(UserAnswer).where(UserAnswer.attempt_id == user_attempt)
        return (await session.execute(stmt)).scalars().all()

    @classmethod
    async def get_all_test_attempts(cls, user_id: int, session: AsyncSession) -> dict:
        result = {}

        stmt = select(TestAttempt).where(TestAttempt.tg_user_id == user_id)
        for user_attempt in (await session.execute(stmt)).scalars().all():
            stmt = select(Test).where(Test.id == user_attempt.test_id)
            test = (await session.execute(stmt)).scalars().first()

            result[user_attempt] = test

        return result


class AnswerDAO(BaseDAO):
    model = Answer


class UserAnswerDAO(BaseDAO):
    model = UserAnswer

