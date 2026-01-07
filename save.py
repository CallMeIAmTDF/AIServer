import subprocess
import glob
import os
import re


def run_moss_on_folder(folder_path: str, language: str = "python") -> str | None:
    files = glob.glob(os.path.join(folder_path, "*.*"))
    if not files:
        return None

    # Gọi moss.pl
    cmd = ["perl", "moss.pl", "-l", language] + files

    print({"cmd": cmd})
    result = subprocess.run(cmd, capture_output=True, text=True)
    match = re.search(r"(http://moss\.stanford\.edu/results/\d+/\d+)", result.stdout)
    if match:
        return match.group(1)
    else:
        return None
#
# link = run_moss_on_folder("submission/contest_1/problem_102/java", "java")
# print(link)
