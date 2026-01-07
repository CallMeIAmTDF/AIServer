from typing import List

from pydantic import BaseModel


class CreateBasicCodeAnalysis(BaseModel):
    code: str


class InDepthCodeAnalysis(BaseModel):
    code: str
    status: str


class CreateInDepthCodeAnalysis(BaseModel):
    codes: List[InDepthCodeAnalysis]
