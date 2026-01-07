from typing import List

from pydantic import BaseModel

from model.contest import Contest
from model.submission import Submission


class ContestRequest(BaseModel):
    contest: Contest
    submissions: List[Submission]
