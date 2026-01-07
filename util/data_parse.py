import json
import re
from copy import deepcopy


def loadGeminiResponse(response, structure: dict):
    """Parse & normalize JSON từ Gemini API."""
    try:
        text = response["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = re.sub(r"^```json\s*|\s*```$", "", text)
        data = json.loads(text)
    except Exception:
        data = {}
    return normalize_json(data, structure)


def loadGroqResponse(response, structure: dict):
    """Parse & normalize JSON từ Groq API."""
    # print({"content": response.choices[0].message.content.strip()})
    try:
        text = response.choices[0].message.content.strip()
        try:
            data = json.loads(text)
            # print({"data": data})
        except json.JSONDecodeError:
            match = re.search(r'```json(.*?)```', text, re.S)
            if match:
                data = json.loads(match.group(1).strip())
            else:
                data = {}
    except Exception:
        data = {}
    return normalize_json(data, structure)


def normalize_json(text_or_dict, structure: dict):
    """
    Chuẩn hóa dữ liệu JSON trả về từ LLM theo cấu trúc mong muốn.

    Args:
        text_or_dict (str | dict): chuỗi JSON hoặc dict gốc (có thể sai cấu trúc)
        structure (dict): cấu trúc mẫu mong muốn (có thể lồng nhau)

    Returns:
        dict: dữ liệu đã chuẩn hóa theo cấu trúc
    """
    if isinstance(text_or_dict, str):
        raw = text_or_dict.strip()
        match = re.search(r'```json(.*?)```', raw, re.S)
        if match:
            raw = match.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}
    elif isinstance(text_or_dict, dict):
        data = text_or_dict
    else:
        data = {}

    def fill_missing(d, template):
        if not isinstance(template, dict):
            return d if d is not None else template

        result = {}
        for key, sub_template in template.items():
            value = d.get(key) if isinstance(d, dict) else None
            if isinstance(sub_template, dict):
                result[key] = fill_missing(value if isinstance(value, dict) else {}, sub_template)
            else:
                if isinstance(sub_template, list):
                    if isinstance(value, list):
                        result[key] = value
                    else:
                        result[key] = []
                else:
                    result[key] = value if value is not None else sub_template
        return result

    return fill_missing(data, deepcopy(structure))
