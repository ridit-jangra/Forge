import os
import json
import datetime
from pathlib import Path
from .config import FOLDER_PATH

def get_new_commit_id() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

def ensure_repo() -> None:
    if not os.path.exists(FOLDER_PATH):
        raise Exception("Init a repo first.")

def init_repo_local(repo_name: str) -> None:
    if os.path.exists(FOLDER_PATH):
        print("Repo is already initialized")
        return

    os.mkdir(FOLDER_PATH)

    (Path(FOLDER_PATH) / "files.json").write_text("[]", encoding="utf-8")
    (Path(FOLDER_PATH) / "commits.json").write_text("[]", encoding="utf-8")
    (Path(FOLDER_PATH) / "repo.json").write_text(json.dumps({"name": repo_name}), encoding="utf-8")
    (Path(FOLDER_PATH) / "current_commit.txt").write_text("", encoding="utf-8")

    init_commit_id = get_new_commit_id()
    commits_data = [{"id": init_commit_id, "message": "Init commit.", "files": []}]
    (Path(FOLDER_PATH) / "commits.json").write_text(json.dumps(commits_data), encoding="utf-8")
    (Path(FOLDER_PATH) / "current_commit.txt").write_text(init_commit_id, encoding="utf-8")

    print(f"[Local] Repository '{repo_name}' initialized successfully!")
    print("[Local] Use 'forge push' to create the repository on the server.")

def get_repo_name() -> str:
    data = json.loads((Path(FOLDER_PATH) / "repo.json").read_text(encoding="utf-8"))
    return data["name"]

def load_file_data() -> list:
    try:
        return json.loads((Path(FOLDER_PATH) / "files.json").read_text(encoding="utf-8"))
    except:
        return []

def save_file_data(entries: list) -> None:
    (Path(FOLDER_PATH) / "files.json").write_text(json.dumps(entries), encoding="utf-8")

def load_commit_data() -> list:
    try:
        return json.loads((Path(FOLDER_PATH) / "commits.json").read_text(encoding="utf-8"))
    except:
        return []

def save_commit_data(entries: list) -> None:
    (Path(FOLDER_PATH) / "commits.json").write_text(json.dumps(entries), encoding="utf-8")

def get_current_commit() -> str:
    return (Path(FOLDER_PATH) / "current_commit.txt").read_text(encoding="utf-8")

def set_current_commit(commit_id: str) -> None:
    (Path(FOLDER_PATH) / "current_commit.txt").write_text(commit_id, encoding="utf-8")

def get_commit(commit_id: str) -> dict:
    for c in load_commit_data():
        if c.get("id") == commit_id:
            return c
    return {}

def add_file_entry(path: str, content: str) -> None:
    ensure_repo()
    entries = load_file_data()
    entries = [e for e in entries if e.get("file_path") != path]

    status = "new"
    if os.path.exists(path):
        try:
            existing = Path(path).read_text(encoding="utf-8", errors="ignore")
            if existing != content:
                status = "modified"
        except:
            pass

    entries.append({"file_path": path, "file_content": content, "status": status})
    save_file_data(entries)

def remove_file_entry(entry_file_path: str) -> None:
    ensure_repo()
    entries = load_file_data()
    for e in list(entries):
        if e.get("file_path") == entry_file_path:
            entries.remove(e)
            entries.append({"file_path": e.get("file_path"), "file_content": e.get("file_content"), "status": "remove"})
            break
    save_file_data(entries)

def add_commit(message: str) -> None:
    ensure_repo()
    commit_id = get_new_commit_id()
    files = load_file_data()
    commits = load_commit_data()
    commits.append({"id": commit_id, "message": message, "files": files})
    save_commit_data(commits)
    set_current_commit(commit_id)
