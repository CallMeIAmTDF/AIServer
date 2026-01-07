from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import datetime


class DifficultyEnum(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ProblemCategoryEnum(str, Enum):
    ARRAY = "ARRAY"
    STRING = "STRING"
    HASH_TABLE = "HASH_TABLE"
    DYNAMIC_PROGRAMMING = "DYNAMIC_PROGRAMMING"
    MATH = "MATH"
    SORTING = "SORTING"
    GREEDY = "GREEDY"
    DEPTH_FIRST_SEARCH = "DEPTH_FIRST_SEARCH"
    BINARY_SEARCH = "BINARY_SEARCH"
    DATABASE = "DATABASE"
    MATRIX = "MATRIX"
    TREE = "TREE"
    BREADTH_FIRST_SEARCH = "BREADTH_FIRST_SEARCH"
    BIT_MANIPULATION = "BIT_MANIPULATION"
    TWO_POINTERS = "TWO_POINTERS"
    PREFIX_SUM = "PREFIX_SUM"
    HEAP = "HEAP"
    SIMULATION = "SIMULATION"
    BINARY_TREE = "BINARY_TREE"
    GRAPH = "GRAPH"
    STACK = "STACK"
    COUNTING = "COUNTING"
    SLIDING_WINDOW = "SLIDING_WINDOW"
    DESIGN = "DESIGN"
    ENUMERATION = "ENUMERATION"
    BACKTRACKING = "BACKTRACKING"
    UNION_FIND = "UNION_FIND"
    LINKED_LIST = "LINKED_LIST"
    NUMBER_THEORY = "NUMBER_THEORY"
    ORDERED_SET = "ORDERED_SET"
    MONOTONIC_STACK = "MONOTONIC_STACK"
    SEGMENT_TREE = "SEGMENT_TREE"
    TRIE = "TRIE"
    COMBINATORICS = "COMBINATORICS"
    BITMASK = "BITMASK"
    QUEUE = "QUEUE"
    RECURSION = "RECURSION"
    DIVIDE_AND_CONQUER = "DIVIDE_AND_CONQUER"
    BINARY_INDEXED_TREE = "BINARY_INDEXED_TREE"
    MEMOIZATION = "MEMOIZATION"
    GEOMETRY = "GEOMETRY"
    HASH_FUNCTION = "HASH_FUNCTION"
    BINARY_SEARCH_TREE = "BINARY_SEARCH_TREE"
    STRING_MATCHING = "STRING_MATCHING"
    SHORTEST_PATH = "SHORTEST_PATH"
    TOPOLOGICAL_SORT = "TOPOLOGICAL_SORT"
    ROLLING_HASH = "ROLLING_HASH"
    GAME_THEORY = "GAME_THEORY"
    INTERACTIVE = "INTERACTIVE"
    DATA_STREAM = "DATA_STREAM"
    MONOTONIC_QUEUE = "MONOTONIC_QUEUE"
    BRAINTEASER = "BRAINTEASER"
    DOUBLY_LINKED_LIST = "DOUBLY_LINKED_LIST"
    RANDOMIZED = "RANDOMIZED"
    MERGE_SORT = "MERGE_SORT"
    COUNTING_SORT = "COUNTING_SORT"
    ITERATOR = "ITERATOR"
    CONCURRENCY = "CONCURRENCY"
    PROBABILITY_AND_STATISTICS = "PROBABILITY_AND_STATISTICS"
    QUICKSELECT = "QUICKSELECT"
    SUFFIX_ARRAY = "SUFFIX_ARRAY"
    LINE_SWEEP = "LINE_SWEEP"
    MINIMUM_SPANNING_TREE = "MINIMUM_SPANNING_TREE"
    BUCKET_SORT = "BUCKET_SORT"
    SHELL = "SHELL"
    RESERVOIR_SAMPLING = "RESERVOIR_SAMPLING"
    STRONGLY_CONNECTED_COMPONENT = "STRONGLY_CONNECTED_COMPONENT"
    EULERIAN_CIRCUIT = "EULERIAN_CIRCUIT"
    RADIX_SORT = "RADIX_SORT"
    REJECTION_SAMPLING = "REJECTION_SAMPLING"
    BICONNECTED_COMPONENT = "BICONNECTED_COMPONENT"


class TestCase(BaseModel):
    id: int
    input: str
    expectedOutput: str = Field(alias="expectedOutput")
    isHidden: Optional[bool] = Field(default=False, alias="isHidden")

    class Config:
        populate_by_name = True


class Hint(BaseModel):
    id: int
    description: str


class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    constrains: Optional[str] = None
    followUp: Optional[str] = Field(default=None, alias="followUp")
    timeLimit: Optional[int] = Field(default=None, alias="timeLimit")
    memoryLimit: Optional[int] = Field(default=None, alias="memoryLimit")
    difficulty: Optional[DifficultyEnum] = None
    point: Optional[int] = None
    categories: Optional[List[ProblemCategoryEnum]] = []
    hints: Optional[List[Hint]] = []
    allTestCases: Optional[List[TestCase]] = Field(default=[], alias="allTestCases")

    class Config:
        populate_by_name = True


class ContestDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    password: Optional[str] = None
    startTime: Optional[datetime] = Field(default=None, alias="startTime")
    endTime: Optional[datetime] = Field(default=None, alias="endTime")
    problems: List[ProblemResponse] = []

    class Config:
        populate_by_name = True
