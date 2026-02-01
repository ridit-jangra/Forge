import os
import json
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import SERVER_URL, DEFAULT_TIMEOUT, FOLDER_PATH
from ..session import get_auth_headers
from ..http import safe_json
from .. import repo_store as store

def init_repo() -> None:
    headers = get_auth_headers()
    if not headers:
        print("[Error] You must be logged in to initialize a repo")
        return
    store.init_repo_local(Path.cwd().name)

def add(path: str) -> None:
    store.ensure_repo()
    if path == ".":
        add_all()
        return

    p = Path(path)
    if not p.exists():
        print("[Error] File not found")
        return

    content = p.read_text(encoding="utf-8", errors="ignore")
    store.add_file_entry(path, content)

def add_all() -> None:
    store.ensure_repo()
    repo_root = Path.cwd().resolve()

    ignore_paths = [".forge"]
    if Path(".forgeignore").exists():
        ignore_paths += [line.strip() for line in Path(".forgeignore").read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]

    ignore_set = {(repo_root / p).resolve() for p in ignore_paths}

    def ignored(p: Path) -> bool:
        p = p.resolve()
        return any(p.is_relative_to(x) for x in ignore_set)

    current_commit = store.get_commit(store.get_current_commit())
    tracked = {f.get("file_path"): f for f in (current_commit.get("files") or [])}

    for root, dirs, files in os.walk(repo_root):
        root_p = Path(root)
        dirs[:] = [d for d in dirs if not ignored(root_p / d)]

        existing = {(root_p / f).resolve().relative_to(repo_root).as_posix() for f in files}

        for tracked_path in list(tracked.keys()):
            norm = str(tracked_path).replace("\\", "/").lstrip("./")
            if norm not in existing and ".forge" not in norm:
                store.remove_file_entry(tracked_path)
                tracked.pop(tracked_path, None)

        for name in files:
            abs_path = root_p / name
            if ignored(abs_path) and abs_path.name != ".forgeignore":
                continue

            rel = abs_path.resolve().relative_to(repo_root).as_posix()
            try:
                content = abs_path.read_text(encoding="utf-8", errors="ignore")
                store.add_file_entry(rel, content)
            except:
                pass

def commit(message: str) -> None:
    store.add_commit(message)

def checkout(commit_id: str) -> None:
    store.ensure_repo()
    if commit_id == "-":
        commit_id = store.get_current_commit()
    c = store.get_commit(commit_id)
    files = c.get("files") or []
    for f in files:
        path = f.get("file_path")
        if not path:
            continue
        status = f.get("status")
        if status == "remove":
            try:
                os.remove(path)
            except:
                pass
            continue
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(f.get("file_content") or "", encoding="utf-8", errors="strict")

def push() -> None:
    headers = get_auth_headers()
    if not headers:
        print("[Error] Not logged in. Please run 'forge login' first.")
        return

    commit_id = store.get_current_commit()
    commit = store.get_commit(commit_id) or {}
    repo_name = store.get_repo_name()

    commits_data = store.load_commit_data() or []
    files_data = store.load_file_data() or []

    init_data = {"name": repo_name, "commits": commits_data, "files": files_data}
    init_resp = requests.post(f"{SERVER_URL}/api/repos/init", json=init_data, headers=headers, timeout=DEFAULT_TIMEOUT)

    if init_resp.status_code == 200:
        print("[Remote] Repository created on server")
    elif init_resp.status_code == 400:
        print("[Remote] Using existing repository")
    else:
        print(f"[Error] Failed to initialize repo: {init_resp.status_code} {(init_resp.text or '')[:200]}")
        return

    commit_payload = {"id": commit.get("id"), "message": commit.get("message"), "files": commit.get("files"), "repo_name": repo_name}
    resp = requests.post(f"{SERVER_URL}/api/repos/commits/add", json=commit_payload, headers=headers, timeout=DEFAULT_TIMEOUT)
    print(f"[Remote] (Commit Changes) {safe_json(resp)}")

    resp = requests.post(f"{SERVER_URL}/api/repos/files/reset", json={"repo_name": repo_name}, headers=headers, timeout=DEFAULT_TIMEOUT)
    print(f"[Remote] (File Reset) {safe_json(resp)}")

    files_entries = store.load_file_data() or []
    total = len(files_entries)

    def upload_one(file_entry: dict):
        payload = {
            "path": file_entry.get("file_path"),
            "content": file_entry.get("file_content"),
            "repo_name": repo_name,
            "status": file_entry.get("status")
        }
        r = requests.post(f"{SERVER_URL}/api/repos/files/add", json=payload, headers=headers, timeout=40)
        return safe_json(r)

    max_workers = min(16, max(4, (os.cpu_count() or 8)))
    started = time.time()
    failures = 0

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(upload_one, fe) for fe in files_entries]
        done = 0
        for fut in as_completed(futures):
            try:
                fut.result()
                done += 1
                if done % 25 == 0 or done == total:
                    elapsed = time.time() - started
                    rate = done / elapsed if elapsed > 0 else done
                    print(f"[Remote] Uploaded {done}/{total} files ({rate:.1f}/s)")
            except:
                failures += 1

    if failures:
        print(f"[Error] {failures} file(s) failed to upload.")
        return

    resp = requests.post(
        f"{SERVER_URL}/api/repos/commits/set_current",
        json={"repo_name": repo_name, "commit_id": commit_id},
        headers=headers,
        timeout=DEFAULT_TIMEOUT
    )
    print(f"[Remote] (Current Commit Changes) {safe_json(resp)}")

    resp = requests.post(
        f"{SERVER_URL}/api/repos/push",
        json={"repo_name": repo_name, "commit_id": commit.get('id')},
        headers=headers,
        timeout=DEFAULT_TIMEOUT
    )
    print(f"[Remote] (Push Changes) {safe_json(resp)}")

    print("[Local] (Push Complete) Done")

def clone(repo_full_name: str, dir_path: str = "") -> None:
    headers = get_auth_headers()

    if "/" not in repo_full_name:
        print("[Error] Please specify repo in format: owner_id/repo_name")
        return

    owner_id, repo_name = repo_full_name.split("/", 1)
    response = requests.post(f"{SERVER_URL}/api/repos/clone", json={"repo_name": repo_name, "owner_id": owner_id}, headers=headers, timeout=DEFAULT_TIMEOUT)

    if response.status_code != 200:
        try:
            print("[Remote] Error:", response.json().get("detail", "Repo not found"))
        except:
            print("[Remote] Error:", response.text[:200])
        return

    data = response.json()
    if data.get("status") != "ok":
        print("[Remote] Error:", data.get("message", "Repo not found"))
        return

    print(f"[Remote] (Found Repo) {owner_id}/{repo_name}")
    if data.get("is_fork"):
        print(f"[Remote] (Fork) This is a fork of {data.get('forked_from')}")
    print("[Remote] (Starting Cloning) Starting...")

    files = data["files"]
    commits = data["commits"]
    current_commit = data["current_commit_id"]

    if dir_path == "":
        dir_path = repo_name

    Path(dir_path).mkdir()
    Path(dir_path, ".forge").mkdir()
    repo_path = str(Path.cwd() / dir_path)

    Path(dir_path, ".forge", "files.json").write_text(json.dumps(files), encoding="utf-8")
    Path(dir_path, ".forge", "commits.json").write_text(json.dumps(commits), encoding="utf-8")
    Path(dir_path, ".forge", "current_commit.txt").write_text(current_commit, encoding="utf-8")
    Path(dir_path, ".forge", "repo.json").write_text(json.dumps({
        "name": repo_name,
        "path": repo_path,
        "original_owner": owner_id,
        "cloned_from": f"{owner_id}/{repo_name}"
    }), encoding="utf-8")

    for file in files:
        rel = file.get("file_path") or ""
        file_path = Path(dir_path) / rel
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file.get("file_content") or "", encoding="utf-8", errors="strict")
        print(f"[Remote] (Fetching File) {rel}...")

    print("[Local] (Completed Cloning) Completed...")
    print(f"[Local] cd {dir_path} to continue.")
