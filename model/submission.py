from pydantic import BaseModel


class Submission(BaseModel):
    username: str
    code: str
    language: str
    pid: int
    pTitle: str
