import datetime

from pydantic import BaseModel


class SubmitTest(BaseModel):
    test_id: int
    username: str
    lastname: str
    city: str
    user_id: int
    started_at: datetime.datetime | str
    completed_at: datetime.datetime | str
    answers: list[str]


class CreateTest(BaseModel):
    test_name: str
    open_questions: int
    close_questions: int
    test_time: int
    start_time: datetime.datetime | str
    end_time: datetime.datetime | str
    is_ended: bool
    user_id: int
    answer: list[dict]
