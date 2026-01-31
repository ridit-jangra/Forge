from fastapi import FastAPI, HTTPException, Body
from pathlib import Path
from pydantic import BaseModel
import json
import os

app = FastAPI()

ROOT = Path(".")
REPOS = ROOT / "repos"
REPOS.mkdir(parents=True, exist_ok=True)

def load_file_data(repo_name: str) -> list:
    data = []
    file_path = f"repos/{repo_name}/.forge/files.json"

    try:
        with open(file_path, "r") as f:
            data = json.loads(f.read())
    except Exception as e:
        print(f"Error occured: ${e}")
        return

    return data

def load_commit_data(repo_name: str) -> list:
    data = []
    file_path = f"repos/{repo_name}/.forge/commits.json"

    try:
        with open(file_path, "r") as f:
            data = json.loads(f.read())
    except Exception as e:
        print(f"Error occured: ${e}")
        return

    return data

def load_commit_data_by_id(repo_name: str, commit_id: str) -> dict:
    data = {}
    file_path = f"repos/{repo_name}/.forge/commits.json"

    try:
        with open(file_path, "r") as f:
            commits = json.loads(f.read())
            for commit in commits:
                if commit.get("id") == commit_id:
                    data = commit
    except Exception as e:
        print(f"Error occured: ${e}")
        return

    return data

def get_current_commit_id(repo_name: str) -> str:
    file_path = f"repos/{repo_name}/.forge/current_commit.txt"
    commit_id = ""

    try:
        with open(file_path, "r") as f:
            commit_id = f.read()
    except Exception as e:
        print(f"Error occured: ${e}")
        return
    
    return commit_id

def set_current_commit_id(repo_name: str, commit_id: str) -> None:
    file_path = f"repos/{repo_name}/.forge/current_commit.txt"

    try:
        with open(file_path, "w") as f:
            f.write(commit_id)
    except Exception as e:
        print(f"Error occured: ${e}")
        return

class RepoData(BaseModel):
    name: str
    path: str
    commits: list
    files: list

class FileData(BaseModel):
    path: str
    content: str
    status: str
    repo_name: str
    status: str

class CommitData(BaseModel):
    id: str
    message: str
    repo_name: str
    files: list

class CurrentCommitData(BaseModel):
    commit_id: str
    repo_name: str

class ResetFilesData(BaseModel):
    repo_name: str

class PushData(BaseModel):
    repo_name: str
    commit_id: str

class CloneData(BaseModel):
    repo_name: str

@app.post("/repos/init")
def init_repo(repo: RepoData):
    name = repo.name
    repo_path = REPOS / name / ".forge"
    if repo_path.exists():
        raise HTTPException(400, "Repo already exists")

    repo_path.mkdir(parents=True, exist_ok=False)
    (repo_path / "files.json").write_text(json.dumps(repo.files))
    (repo_path / "commits.json").write_text(json.dumps(repo.commits))
    (repo_path / "repo.json").write_text(json.dumps({"name": repo.name, "path": repo.path}))

    return {"status": "ok", "repo": name}

@app.post("/repos/files/reset")
def reset_files(data: ResetFilesData):
    try:
        with open(f"repos/{data.repo_name}/.forge/files.json", "w") as f:
            f.write("[]")
        
    except Exception as e:
        print(f"Error occured: {e}")

    return {"status": "ok", "done": "true"}

@app.post("/repos/files/add")
def add_file(file: FileData):
    path = file.path
    content = file.content
    repo_name = file.repo_name
    status = file.status

    files_entries = load_file_data(repo_name)
    files_entries = [f for f in files_entries if f.get("file_path") != path]
    
    files_entries.append({
        "file_path": path,
        "file_content": content,
        "status": status
    })

    try:
        with open(f"repos/{repo_name}/.forge/files.json", "w") as f:
            f.write(json.dumps(files_entries))
        
    except Exception as e:
        print(f"Error occured: {e}")

    return {"status": "ok", "path": path}


@app.post("/repos/commits/set_current")
def set_current_commit(current_commit: CurrentCommitData):
    repo_name = current_commit.repo_name
    commit_id = current_commit.commit_id
    set_current_commit_id(repo_name, commit_id)

@app.post("/repos/commits/add")
def add_commit_remote(commit: CommitData):
    id = commit.id
    message = commit.message
    files = commit.files
    repo_name = commit.repo_name
    
    commit_entries = load_commit_data(repo_name)
    new_commit_entry = {"id": id, "message": message, "files": files}

    file_path = f"repos/{repo_name}/.forge/commits.json"

    for commit_entry in commit_entries:
        if commit_entry.get("message") == message:
            return {"status": "error", "message": "Commit already exists."}
        
    commit_entries.append(new_commit_entry)
    
    try:
        with open(file_path, "w") as f:
            f.write(json.dumps(commit_entries, indent=2))
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "ok", "commit": message}

@app.post("/repos/push")
def push(data: PushData):
    repo_name = data.repo_name
    commit_id = data.commit_id
    commit_data = load_commit_data_by_id(repo_name, commit_id)
    files = commit_data.get("files", [])

    for file in files:
        try:
            file_path = Path(f"repos/{repo_name}") / file.get("file_path")

            file_path.parent.mkdir(parents=True, exist_ok=True)

            content = file.get("file_content") or ""
            file_path.write_text(content)

        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "ok", "done": "true"}

@app.post("/repos/clone")
def clone_repo(data: CloneData):
    repo_name = data.repo_name
    repo_path = REPOS / repo_name / ".forge"

    if not repo_path.exists():
        raise HTTPException(404, f"Repo '{repo_name}' not found")

    files = []
    files_path = repo_path / "files.json"
    if files_path.exists():
        with open(files_path, "r") as f:
            files = json.load(f)

    commits = []
    commits_path = repo_path / "commits.json"
    if commits_path.exists():
        with open(commits_path, "r") as f:
            commits = json.load(f)
    
    current_commit_id =  get_current_commit_id(repo_name)

    return {
        "status": "ok",
        "repo_name": repo_name,
        "files": files,
        "commits": commits,
        "current_commit_id":current_commit_id
    }
