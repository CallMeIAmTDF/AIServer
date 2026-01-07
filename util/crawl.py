import os

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def getMetaData(url: str):
    """
    :param url:
    :return: filename1, filename2, numofsimline
    :e.g: [('submissions\\thaidang_1_23213231.py (98%)', 'submissions\\thaidang_1_3212321.py (98%)', 18)]
    """
    soup = getSoup(url)
    table = soup.find('table')
    results = []
    if table:
        rows = table.find_all("tr")
        anchors = table.find_all("a")
        numbers = table.select("td[align=right]")
        if len(rows) > 1:
            for i, num_td in enumerate(numbers):
                file1 = anchors[2 * i].get_text(strip=True)
                file2 = anchors[2 * i + 1].get_text(strip=True)
                match = re.search(r"\d+", num_td.get_text())
                lines = int(match.group()) if match else None
                results.append({
                    "file1": file1,
                    "file2": file2,
                    "lines": lines,
                })
    return results


def getCodeAndColor(url: str):
    """
        :param url:
        :return: [{color, code}]
        :e.g: [{'color': '#FF0000', 'code': 'def is_prime(num):\n    if num < 2:\n        return False\n    for j in range(2, int(num ** 0.5) + 1):\n        if num % j == 0:\n            return False\n    return True\n\ndef sum_primes(n):\n    total = 0\n    for i in range(1, n + 1):\n        if is_prime(i):\n            total += i\n    return total\n\nn = int(input("Nhập số n: "))\nresult = sum_primes(n)\nprint(f"Tổng các số nguyên tố từ 1 đến {n} là: {result}")'}]
        """
    soup = getSoup(url)
    pre = soup.find('pre')
    fonts = pre.find_all('font')

    res = []
    for font in fonts:
        res.append({
            "color": font["color"],
            "code": font.get_text(strip=True),
        })
    return res


def getMatchLine(url: str):
    soup = getSoup(url)
    table = soup.find('table')
    tr = table.find_all('tr')[1]
    anchors = tr.find_all("a")
    numbers = [a.get_text(strip=True) for a in anchors if a.get_text(strip=True)]
    print(numbers)


def getSoup(url: str):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup


def process_item(base_url, i, data):
    if base_url[-1] != "/":
        base_url += "/"
    left = getCodeAndColor(f"{base_url}match{i}-0.html")
    right = getCodeAndColor(f"{base_url}match{i}-1.html")
    return {
        "file1": {"filename": data["file1"], "source": left},
        "file2": {"filename": data["file2"], "source": right},
        "lines": data["lines"],
    }


def crawl(base_urls, filename):
    # base_url = "http://moss.stanford.edu/results/3/2851446376621/"
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    RESULT_DIR = os.path.join(BASE_DIR, "result")
    os.makedirs(RESULT_DIR, exist_ok=True)
    result = []
    for base_url in base_urls:
        metadata = getMetaData(base_url)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_item, base_url, i, data) for i, data in enumerate(metadata)]
            for future in as_completed(futures):
                result.append(future.result())
    with open(os.path.join(RESULT_DIR, f"{filename}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    return result
