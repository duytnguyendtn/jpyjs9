from contextlib import closing
from io import BytesIO
from pathlib import Path
import shutil
from sys import prefix
from zipfile import ZipFile

import requests

print("(clone_js9.py) Hello world!")
venv_src_path = Path(prefix) / "src"
js9_path = venv_src_path / "js9"

# Remove existing install
if js9_path.exists():
    shutil.rmtree(js9_path)

zip_request = requests.get("https://github.com/duytnguyendtn/js9/zipball/multi")
with closing(zip_request), ZipFile(BytesIO(zip_request.content)) as tmpzip:
    tmpzip.extractall(path=venv_src_path)

# Rename Github's commit folder to our standard js9 folder
extracted_repo_folders = [i.name for i in venv_src_path.iterdir() if i.name.startswith("duytnguyendtn-js9")]
# There should only be one folder, otherwise, GitHub changed their folder structure and we should stop!
assert len(extracted_repo_folders) == 1
(venv_src_path / extracted_repo_folders[0]).rename(js9_path)