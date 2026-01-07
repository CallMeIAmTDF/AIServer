from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field


class SubmissionSummary(BaseModel):
    passedSubmissions: int
    failedSubmissions: int


class DayOfWeekAnalysis(BaseModel):
    busiestDay: str
    busiestTimeSlot: str


class Stats(BaseModel):
    rank: int
    point: int
    joined: datetime


class LanguageStatusSummary(BaseModel):
    passed: int
    failed: int
    total: int


class UserStatsResponse(BaseModel):
    submissionSummary: SubmissionSummary
    dailyTimeSlotAnalysis: Dict[str, int]
    dayOfWeekAnalysis: DayOfWeekAnalysis
    categorySubmissionCount: Dict[str, int]
    languageSubmissionSummary: Dict[str, LanguageStatusSummary]
    stats: Stats
