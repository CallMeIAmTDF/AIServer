import os

from const.file_extension import EXT_MAP
from model.request.contest_request import ContestRequest


def save_submissions(data: ContestRequest, base_dir="submission"):
    contest_id = data.contest.id
    # problem_id = data.submission

    # lưu toàn bộ submission
    for sub in data.submissions:
        lang = sub.language.lower()
        if lang not in EXT_MAP:
            continue
        problem_id = sub.pid
        problem_name = sub.pTitle
        folder_path = os.path.join(
            base_dir,
            f"contest_{contest_id}",
            f"problem_{problem_id}__tdf__{problem_name}",
            lang
        )
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{sub.username.split('@')[0]}.{EXT_MAP[lang]}"
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sub.code)

        # urls = []
        # for lang, ext in EXT_MAP.items():
        #     folder_path = os.path.join(base_dir, f"contest_{contest_id}", f"problem_{problem_id}", lang)
        #     if os.path.exists(folder_path):
        #         files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        #         if len(files) > 1:
        #             print(f"run moss /contest_{contest_id}/problem_{problem_id}/{lang}")
        #             url = run_moss_on_folder(folder_path, language=lang)
        #             urls.append(url)
        # crawl.crawl(urls)

