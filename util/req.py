import requests
from config.config import settings


def send_call_back(contest_id: int):
    url = f"{settings.api_protocol}://{settings.api_host}:{settings.api_port}/contest/{contest_id}/plagiarism/callback"

    try:
        resp = requests.get(url, timeout=3)
        print(f"Callback OK: {resp.status_code}")
        return True
    except Exception as e:
        print(f"[Callback Failed] {e}")
        return False


def send_upload_file_callback(file_name: str, status: str):
    # /chat/upload/213213123/callback/FAILED
    url = f"{settings.api_protocol}://{settings.api_host}:{settings.api_port}/chat/upload/{file_name}/callback/{status}"
    # url = f"https://webhook.site/8d1434a8-f9e7-4b59-965d-6e8e36239e3a/{file_name}/callback/{status}"
    try:
        resp = requests.get(url, timeout=3)
        print(f"Callback OK: {resp.status_code}")
        return True
    except Exception as e:
        print(f"[Callback Failed] {e}")
        return False
