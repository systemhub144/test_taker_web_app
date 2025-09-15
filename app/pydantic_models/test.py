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
