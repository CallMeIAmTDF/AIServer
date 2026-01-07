from pydantic import BaseModel


class Contest(BaseModel):
    id: int
    title: str
    description: str
