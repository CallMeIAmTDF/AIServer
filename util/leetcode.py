import requests
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional


class LeetCodeCrawlerException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def crawl_leetcode_problem(url: str) -> Dict:
    try:
        slug = _extract_slug_from_url(url)

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
        })

        query = """
            query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                categoryTitle
                topicTags {
                  name
                  slug
                }
                hints
                exampleTestcases
                sampleTestCase
                metaData
              }
            }
            """

        payload = {
            'query': query,
            'variables': {'titleSlug': slug},
            'operationName': 'questionData'
        }

        response = session.post('https://leetcode.com/graphql', json=payload, timeout=10)

        if response.status_code != 200:
            raise LeetCodeCrawlerException(
                f"Không thể lấy dữ liệu của LeetCode.",
                status_code=response.status_code
            )

        data = response.json()

        if 'errors' in data:
            raise LeetCodeCrawlerException(
                f"Lỗi GraphQL",
                status_code=400
            )

        if not data.get('data') or not data['data'].get('question'):
            raise LeetCodeCrawlerException(
                "Không tìm thấy thử thách",
                status_code=404
            )

        question = data['data']['question']
        return _format_problem_data(question)

    except LeetCodeCrawlerException:
        raise
    except requests.exceptions.Timeout:
        raise LeetCodeCrawlerException("Yêu cầu hết thời gian chờ", status_code=504)
    except requests.exceptions.ConnectionError:
        raise LeetCodeCrawlerException("Lỗi kết nối", status_code=503)
    except Exception as e:
        raise LeetCodeCrawlerException(f"Lỗi không mong đợi", status_code=500)


def _extract_slug_from_url(url: str) -> str:
    match = re.search(r'/problems/([^/]+)', url)
    if match:
        return match.group(1).rstrip('/')
    raise LeetCodeCrawlerException("Định dạng URL LeetCode không hợp lệ", status_code=400)


def _format_problem_data(question: Dict) -> Dict:
    """Format the crawled data to match required structure"""

    content = question.get('content', '')

    # Extract all parts first
    follow_up = _extract_follow_up(content)
    constraints = _extract_constraints(content)
    #
    # items = [line.strip() for line in constraints.split("\n") if line.strip()]
    #
    # constraints_html = "<ul>\n" + "\n".join(f"  <li>{item}</li>" for item in items) + "\n</ul>"

    cleaned_description = _clean_description(content)

    # Parse metadata
    metadata_str = question.get('metaData', '{}')
    try:
        metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
    except:
        metadata = {}

    # Parse test cases with expected outputs
    test_cases = _parse_test_cases(
        question.get('exampleTestcases', ''),
        content,
        metadata
    )

    # Format hints
    hints = []
    for hint in question.get('hints', []):
        # Remove HTML tags from hint
        clean_hint = BeautifulSoup(hint, 'html.parser').get_text() if hint else ""
        if clean_hint:
            hints.append({"description": clean_hint})

    # Map difficulty
    difficulty_map = {
        'Easy': 'EASY',
        'Medium': 'MEDIUM',
        'Hard': 'HARD'
    }

    # Categories from topic tags - map to standard format
    topic_tags = question.get('topicTags', [])
    categories = _map_categories([tag['name'] if isinstance(tag, dict) else tag for tag in topic_tags])

    return {
        "title": question.get('title', ''),
        "description": cleaned_description.replace(" ", " "),
        "constrains": constraints.replace(" ", " "),
        "followUp": follow_up.replace(" ", " "),
        "timeLimit": metadata.get('timeout', 2),
        "memoryLimit": metadata.get('memory', 256),
        "difficulty": difficulty_map.get(question.get('difficulty', 'Medium'), 'MEDIUM'),
        "isContestProblem": False,
        "point": _calculate_points(question.get('difficulty', 'Medium')),
        "categories": categories,
        "hints": hints,
        "testCases": test_cases
    }


def _clean_description(content: str) -> str:
    """Clean description by removing examples, constraints, and follow-up sections"""
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')

    # Strategy: Keep only the initial paragraphs before any Example/Constraints/Follow-up
    result_elements = []

    for element in soup.children:
        if not hasattr(element, 'name'):
            continue

        # Get text content to check
        text = element.get_text().strip() if hasattr(element, 'get_text') else ''

        # Stop collecting when we hit Example, Constraints, or Follow-up
        if text and re.search(r'(Example\s*\d*:|Constraints?:|Follow[- ]up:)', text, re.IGNORECASE):
            break

        # Skip if it contains Input:/Output:/Explanation: (part of examples)
        if re.search(r'(Input:|Output:|Explanation:)', text, re.IGNORECASE):
            break

        # Skip empty elements
        if not text:
            continue

        # Keep this element
        result_elements.append(str(element))

    # Join and clean up
    result = '\n'.join(result_elements)

    # Additional cleanup: remove any stray example markers that might be in separate tags
    result = re.sub(r'<p[^>]*>\s*<strong[^>]*>\s*Example\s*\d*:?\s*</strong>\s*</p>', '', result, flags=re.IGNORECASE)
    result = re.sub(r'<strong[^>]*>\s*Example\s*\d*:?\s*</strong>', '', result, flags=re.IGNORECASE)

    # Remove empty paragraphs
    result = re.sub(r'<p>\s*</p>', '', result)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def _map_categories(tags: List[str]) -> List[str]:
    category_map = {
        'Array': 'ARRAY',
        'String': 'STRING',
        'Hash Table': 'HASH_TABLE',
        'Dynamic Programming': 'DYNAMIC_PROGRAMMING',
        'Math': 'MATH',
        'Sorting': 'SORTING',
        'Greedy': 'GREEDY',
        'Depth-First Search': 'DEPTH_FIRST_SEARCH',
        'Binary Search': 'BINARY_SEARCH',
        'Database': 'DATABASE',
        'Matrix': 'MATRIX',
        'Tree': 'TREE',
        'Breadth-First Search': 'BREADTH_FIRST_SEARCH',
        'Bit Manipulation': 'BIT_MANIPULATION',
        'Two Pointers': 'TWO_POINTERS',
        'Prefix Sum': 'PREFIX_SUM',
        'Heap (Priority Queue)': 'HEAP',
        'Simulation': 'SIMULATION',
        'Binary Tree': 'BINARY_TREE',
        'Graph': 'GRAPH',
        'Stack': 'STACK',
        'Counting': 'COUNTING',
        'Sliding Window': 'SLIDING_WINDOW',
        'Design': 'DESIGN',
        'Enumeration': 'ENUMERATION',
        'Backtracking': 'BACKTRACKING',
        'Union Find': 'UNION_FIND',
        'Linked List': 'LINKED_LIST',
        'Number Theory': 'NUMBER_THEORY',
        'Ordered Set': 'ORDERED_SET',
        'Monotonic Stack': 'MONOTONIC_STACK',
        'Segment Tree': 'SEGMENT_TREE',
        'Trie': 'TRIE',
        'Combinatorics': 'COMBINATORICS',
        'Bitmask': 'BITMASK',
        'Queue': 'QUEUE',
        'Recursion': 'RECURSION',
        'Divide and Conquer': 'DIVIDE_AND_CONQUER',
        'Binary Indexed Tree': 'BINARY_INDEXED_TREE',
        'Memoization': 'MEMOIZATION',
        'Geometry': 'GEOMETRY',
        'Hash Function': 'HASH_FUNCTION',
        'Binary Search Tree': 'BINARY_SEARCH_TREE',
        'String Matching': 'STRING_MATCHING',
        'Shortest Path': 'SHORTEST_PATH',
        'Topological Sort': 'TOPOLOGICAL_SORT',
        'Rolling Hash': 'ROLLING_HASH',
        'Game Theory': 'GAME_THEORY',
        'Interactive': 'INTERACTIVE',
        'Data Stream': 'DATA_STREAM',
        'Monotonic Queue': 'MONOTONIC_QUEUE',
        'Brainteaser': 'BRAINTEASER',
        'Doubly-Linked List': 'DOUBLY_LINKED_LIST',
        'Randomized': 'RANDOMIZED',
        'Merge Sort': 'MERGE_SORT',
        'Counting Sort': 'COUNTING_SORT',
        'Iterator': 'ITERATOR',
        'Concurrency': 'CONCURRENCY',
        'Probability and Statistics': 'PROBABILITY_AND_STATISTICS',
        'Quickselect': 'QUICKSELECT',
        'Suffix Array': 'SUFFIX_ARRAY',
        'Line Sweep': 'LINE_SWEEP',
        'Minimum Spanning Tree': 'MINIMUM_SPANNING_TREE',
        'Bucket Sort': 'BUCKET_SORT',
        'Shell': 'SHELL',
        'Reservoir Sampling': 'RESERVOIR_SAMPLING',
        'Strongly Connected Component': 'STRONGLY_CONNECTED_COMPONENT',
        'Eulerian Circuit': 'EULERIAN_CIRCUIT',
        'Radix Sort': 'RADIX_SORT',
        'Rejection Sampling': 'REJECTION_SAMPLING',
        'Biconnected Component': 'BICONNECTED_COMPONENT'
    }

    mapped_categories = []
    for tag in tags:
        if tag in category_map:
            mapped_categories.append(category_map[tag])

    return mapped_categories


def _parse_test_cases(example_testcases: str, content: str, metadata: Dict) -> List[Dict]:
    if not example_testcases:
        return []

    test_cases = []
    input_lines = [line.strip() for line in example_testcases.strip().split('\n') if line.strip()]

    outputs = _extract_outputs_from_content(content)

    params = metadata.get('params', [])

    if not params or len(params) == 0:
        for i, input_line in enumerate(input_lines):
            raw_input = _convert_to_raw_format(input_line)

            test_cases.append({
                "input": raw_input,
                "expectedOutput": outputs[i] if i < len(outputs) else "",
                "isHidden": False
            })
    else:
        num_params = len(params)
        output_idx = 0

        for i in range(0, len(input_lines), num_params):
            if i + num_params <= len(input_lines):
                raw_inputs = [
                    _convert_to_raw_format(input_lines[i + j])
                    for j in range(num_params)
                ]
                combined_input = '\n'.join(raw_inputs)

                test_cases.append({
                    "input": combined_input,
                    "expectedOutput": outputs[output_idx] if output_idx < len(outputs) else "",
                    "isHidden": False
                })
                output_idx += 1

    return test_cases


def _convert_to_raw_format(input_str: str) -> str:
    input_str = input_str.strip()

    if input_str.startswith('[') and input_str.endswith(']'):
        inner = input_str[1:-1]
        return re.sub(r',\s*', ' ', inner)

    if input_str.startswith('"') and input_str.endswith('"'):
        return input_str[1:-1]

    return input_str


def _extract_outputs_from_content(content: str) -> List[str]:
    outputs = []

    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()

    output_matches = re.finditer(r'Output:\s*([^\n]+)', text, re.IGNORECASE)

    for match in output_matches:
        output = match.group(1).strip()
        raw_output = _convert_to_raw_format(output)
        outputs.append(raw_output)

    return outputs


def _extract_constraints(content: str) -> str:
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()

    patterns = [
        r'Constraints?:\s*\n((?:[^\n]+\n)+?)(?:\n\n|Follow-up|Example|\Z)',
        r'Constraints?:\s*([^\n]+(?:\n(?!Example|Follow-up)[^\n]+)*)',
        r'Constraints?:(.+?)(?=(?:Follow-up|Example|$))',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            constraints_text = match.group(1).strip()
            constraints_text = BeautifulSoup(constraints_text, 'html.parser').get_text()
            lines = [line.strip() for line in constraints_text.split('\n') if line.strip()]
            if lines:
                fixed_lines = []
                for line in lines:
                    line = re.sub(r'\b10(\d)\b', r'10^\1', line)
                    fixed_lines.append(line)
                return '\n'.join(fixed_lines)

    return ""


def _extract_follow_up(content: str) -> Optional[str]:
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()

    follow_up_match = re.search(
        r'Follow[- ]up:?\s*(.+?)(?:\n\n|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if follow_up_match:
        follow_up_text = follow_up_match.group(1).strip()
        follow_up_text = BeautifulSoup(follow_up_text, 'html.parser').get_text()
        return follow_up_text

    return None


def _calculate_points(difficulty: str) -> int:
    points_map = {
        'Easy': 100,
        'Medium': 200,
        'Hard': 300
    }
    return points_map.get(difficulty, 100)
