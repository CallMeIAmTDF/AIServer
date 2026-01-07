import json
from typing import List

from const.prompt import BASIC_CODE_ANALYSIS, IN_DEPTH_CODE_ANALYSIS, PROFILE_SUMMARY
from model.request.user_request import InDepthCodeAnalysis
from model.stats_model.stats import UserStatsResponse


def getBasicCodeAnalysis(code) -> str:
    return BASIC_CODE_ANALYSIS.replace("<<INPUT_CODE>>", code)


def getInDepthCodeAnalysis(codes: List[InDepthCodeAnalysis]) -> str:
    codes_str = json.dumps([code.model_dump() for code in codes], ensure_ascii=False, indent=2)
    return IN_DEPTH_CODE_ANALYSIS.replace("<<INPUT_CODE>>", codes_str)


def getProfileSummary(stats: UserStatsResponse) -> str:
    stats_str = stats.model_dump_json(indent=2)
    return PROFILE_SUMMARY.replace("<<USER_INPUT>>", stats_str)
