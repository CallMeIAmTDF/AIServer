import json
import logging
import os
import shutil
import uuid
from typing import List

from fastapi import FastAPI, BackgroundTasks, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config.ai_config import groq_api, gemini_client
from model.contest_model.contest_model import ContestDetailResponse
from model.rag.ChatRequest import ChatRequest
from model.request.leetcode import CrawlRequest
from model.request.user_request import CreateBasicCodeAnalysis, InDepthCodeAnalysis
from model.stats_model.stats import UserStatsResponse
from model.structure import STRUCTURE_BASIC_CODE_ANALYSIS_RESPONSE, STRUCTURE_IN_DEPTH_CODE_ANALYSIS_RESPONSE, \
    STRUCTURE_PROFILE_SUMMARY_RESPONSE
from service.file_service import upload_file
from service.query_service import query
from util import crawl
from const.file_extension import EXT_MAP
from model.request.contest_request import ContestRequest
from save import run_moss_on_folder
from util.contest_to_pdf import create_pdf_from_contest, get_pdf_path, pdf_exists, delete_pdf
from util.data_parse import loadGroqResponse
from util.leetcode import crawl_leetcode_problem, LeetCodeCrawlerException
from util.prompt_generator import getBasicCodeAnalysis, getInDepthCodeAnalysis, getProfileSummary
from util.req import send_call_back, send_upload_file_callback
from util.save_submission import save_submissions
from util.crawl import crawl
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(debug=True)
PDF_STORAGE_DIR = Path("contest_pdfs")
PDF_STORAGE_DIR.mkdir(exist_ok=True)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

client = gemini_client


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI with CORS!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


def process_submission_in_background(data: ContestRequest, ext_map: dict):
    """
    1. Lưu submissions
    2. Chạy MOSS cho tất cả folder
    3. Crawl kết quả
    4. Xóa folder contest
    """
    save_submissions(data)

    contest_id = data.contest.id
    base_dir = os.path.join("submission", f"contest_{contest_id}")
    moss_urls = []
    moss_json_filename = f"contest_{contest_id}"

    if not os.path.exists(base_dir):
        return

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        for lang in ext_map:
            lang_path = os.path.join(folder_path, lang)
            if os.path.isdir(lang_path) and len(os.listdir(lang_path)) > 1:
                url = run_moss_on_folder(lang_path, lang)
                if url:
                    moss_urls.append(url)
                    print({"url": url})

    crawl(moss_urls, moss_json_filename)

    shutil.rmtree(base_dir)

    send_call_back(data.contest.id)


@app.post("/plagiarism")
def plagiarism(data: ContestRequest, background_tasks: BackgroundTasks):
    # Schedule toàn bộ quá trình ở background
    background_tasks.add_task(process_submission_in_background, data, EXT_MAP)

    # Trả về ngay filename
    moss_json_filename = f"contest_{data.contest.id}"
    return {
        "message": "Received successfully",
        "filename": f"{moss_json_filename}.json",
    }


@app.get("/getPlagiarism")
def get_plagiarism(file: str = Query(...)):
    path = f"result/{file}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# @app.post("/plagiarism")
# def plagiarism(data: ContestRequest, background_tasks: BackgroundTasks):
#     return {"message": "Received successfully", "data": data}


@app.get("/test")
async def test():
    code = """
        def two_sum(nums, target):
            mp = {}
            for i, num in enumerate(nums):
                if num in mp:
                    return mp[num], i
                mp[target - num] = i
            return None
        
        n = int(input())
        nums = [int(i) for i in input().split()]
        target = int(input())
        
        res = two_sum(nums, target)
        if res == None:
            print("None")
        else:
            for i in res:
                print(i, end=" ")
    """
    prompt = getBasicCodeAnalysis(code)
    return await call_groq(prompt, STRUCTURE_BASIC_CODE_ANALYSIS_RESPONSE)


@app.post("/basicCodeAnalysis")
async def basicCodeAnalysis(data: CreateBasicCodeAnalysis):
    print(data)
    prompt = getBasicCodeAnalysis(data.code)
    """
        return call_gemini(prompt, STRUCTURE_BASIC_CODE_ANALYSIS_RESPONSE)
    """

    res = await call_groq(prompt, STRUCTURE_BASIC_CODE_ANALYSIS_RESPONSE)
    # print({"res": res})
    return res

    # return gemini_model.generate_content(data.code)


@app.post("/in-depth")
async def inDepthCodeAnalysis(data: List[InDepthCodeAnalysis]):
    prompt = getInDepthCodeAnalysis(data)
    # print(prompt)
    res = await call_groq(prompt, STRUCTURE_IN_DEPTH_CODE_ANALYSIS_RESPONSE)
    # print({"res": res})
    return res


@app.post("/profile-summary")
async def profile_summary(data: UserStatsResponse):
    prompt = getProfileSummary(data)
    res = await call_groq(prompt, STRUCTURE_PROFILE_SUMMARY_RESPONSE)
    return res


def background_upload_and_notify(
        client,
        file_path: str,
        stored_name: str,
):
    try:
        upload_file(
            client,
            file_path,
            stored_name,
        )
        send_upload_file_callback(stored_name, "UPLOADED")
    except Exception as e:
        send_upload_file_callback(stored_name, "FAILED")


@app.post("/files")
def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_id = uuid.uuid4()
    ext = os.path.splitext(file.filename)[1] or ".pdf"
    stored_name = f"{file_id}{ext}"

    permanent_path = os.path.join(UPLOAD_DIR, stored_name)

    with open(permanent_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(permanent_path)

    background_tasks.add_task(
        background_upload_and_notify,
        client,
        permanent_path,
        stored_name,
    )

    return {
        "status": "RECEIVED",
        "file": stored_name,
        "size": file_size
    }


@app.post("/chat")
def ask(request: ChatRequest):
    answer = query(request.question, client)
    return {"answer": answer}


@app.get("/files/{file_name}")
def download_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream"
    )


@app.get("/new")
async def new():
    return {
        "new": "/files/{file_name}"
    }


async def call_groq(prompt: str, structure):
    resp = await groq_api.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
        max_completion_tokens=8192,
        # reasoning_effort=
        top_p=1,
    )
    return loadGroqResponse(resp, structure)


@app.post("/generate-pdf")
async def generate_pdf(contest: ContestDetailResponse,
                       force: bool = Query(False, description="Force regenerate even if cached")):
    """
    Generate PDF file from contest data with caching
    - If PDF exists and force=False: return cached file
    - If PDF doesn't exist or force=True: generate new PDF
    """
    try:
        pdf_path = get_pdf_path(contest.id)
        if pdf_exists(contest.id) and not force:
            return FileResponse(
                path=pdf_path,
                filename=f"contest_{contest.id}.pdf",
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=contest_{contest.id}.pdf",
                    "X-Cache-Status": "HIT"
                }
            )

        # Generate new PDF
        create_pdf_from_contest(contest, str(pdf_path))

        return FileResponse(
            path=pdf_path,
            filename=f"contest_{contest.id}.pdf",
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=contest_{contest.id}.pdf",
                "X-Cache-Status": "MISS"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.post("/crawl")
async def crawl_problem(request: CrawlRequest):
    try:
        data = crawl_leetcode_problem(request.url)
        return data
    except LeetCodeCrawlerException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@app.post("/regenerate-pdf")
async def regenerate_pdf(contest: ContestDetailResponse):
    """
    Force regenerate PDF (ignore cache)
    """
    return await generate_pdf(contest, force=True)


@app.get("/pdf/{contest_id}")
async def get_pdf(contest_id: int):
    """
    Get cached PDF by contest ID
    Returns 404 if PDF doesn't exist
    """
    if not pdf_exists(contest_id):
        raise HTTPException(
            status_code=404,
            detail=f"PDF for contest {contest_id} not found. Please generate it first."
        )

    pdf_path = get_pdf_path(contest_id)
    return FileResponse(
        path=pdf_path,
        filename=f"contest_{contest_id}.pdf",
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=contest_{contest_id}.pdf"
        }
    )


@app.delete("/pdf/{contest_id}")
async def delete_pdf_endpoint(contest_id: int):
    """
    Delete cached PDF file
    """
    if delete_pdf(contest_id):
        return {
            "success": True,
            "message": f"PDF for contest {contest_id} deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"PDF for contest {contest_id} not found"
        )
