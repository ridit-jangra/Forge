import os
import sys
import json
import datetime
import requests
from pathlib import Path
import getpass
from dotenv import load_dotenv

def resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)

load_dotenv(resource_path(".env"))

folder_name = ".forge"
folder_path = f"./{folder_name}"
server_url = os.getenv("FORGE_SERVER_URL", "http://localhost:8000").rstrip("/")

USER_SESSION_FILE = Path(
    str(Path.home() / os.getenv("FORGE_SESSION"))
).expanduser()


def save_user_session(user_data: dict, token: str) -> None:
    """Save user session to local file"""
    session_data = {
        "user": user_data,
        "token": token,
        "logged_in_at": datetime.datetime.now().isoformat()
    }
    
    USER_SESSION_FILE.write_text(json.dumps(session_data, indent=2))
    print(f"[Local] Session saved")

def load_user_session() -> dict | None:
    """Load user session from local file"""
    if not USER_SESSION_FILE.exists():
        return None
    
    try:
        return json.loads(USER_SESSION_FILE.read_text())
    except:
        return None

def clear_user_session() -> None:
    """Clear user session"""
    if USER_SESSION_FILE.exists():
        USER_SESSION_FILE.unlink()
        print("[Local] Session cleared")

def get_auth_headers() -> dict:
    """Get authentication headers from saved session"""
    session = load_user_session()
    if not session:
        return {}
    
    return {"Authorization": f"Bearer {session['token']}"}

def register_user() -> None:
    """Register a new user with email verification"""
    print("=== Forge Registration ===")
    
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("[Error] Passwords don't match")
        return
    
    if len(password) < 6:
        print("[Error] Password must be at least 6 characters")
        return
    
    # Initiate registration
    try:
        response = requests.post(
            f"{server_url}/api/auth/register/initiate",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        
        if response.status_code != 200:
            try:
                error = response.json().get("detail", "Registration failed")
            except:
                error = f"Server returned {response.status_code}: {response.text[:100]}"
            print(f"[Error] {error}")
            return
        
        data = response.json()
        print(f"[Success] Verification email sent to {email}")
        print("Please check your email for the OTP code.")
        
        # Get OTP from user
        otp = input("Enter OTP: ").strip()
        
        # Complete registration
        response = requests.post(
            f"{server_url}/api/auth/register/verify",
            json={"email": email, "otp": otp},
            timeout=10
        )
        
        if response.status_code != 200:
            try:
                error = response.json().get("detail", "Verification failed")
            except:
                error = f"Server returned {response.status_code}"
            print(f"[Error] {error}")
            return
        
        data = response.json()
        if data.get("status") == "ok":
            user = data.get("user")
            token = data.get("token")
            
            # Save session
            save_user_session(user, token)
            
            print(f"[Success] Account created successfully!")
            print(f"[Success] Logged in as {user['username']}")
        else:
            print("[Error] Registration failed")
    
    except requests.exceptions.Timeout:
        print(f"[Error] Connection timeout - server not responding")
    except requests.exceptions.ConnectionError:
        print(f"[Error] Cannot connect to {server_url} - is the server running?")
    except requests.exceptions.RequestException as e:
        print(f"[Error] Connection failed: {e}")
    except ValueError as e:
        print(f"[Error] Invalid response from server (not JSON): {e}")
    except Exception as e:
        print(f"[Error] {e}")

def login_user() -> None:
    """Login existing user"""
    print("=== Forge Login ===")
    
    username = input("Enter username or email: ").strip()
    password = getpass.getpass("Enter password: ")
    
    try:
        response = requests.post(
            f"{server_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code != 200:
            error = response.json().get("detail", "Login failed")
            print(f"[Error] {error}")
            return
        
        data = response.json()
        if data.get("status") == "ok":
            token = data.get("token")
            
            # Get user info
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{server_url}/api/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json().get("user")
                save_user_session(user_data, token)
                print(f"[Success] Logged in as {user_data['username']}")
            else:
                print("[Error] Failed to get user information")
        else:
            print("[Error] Login failed")
    
    except requests.exceptions.RequestException as e:
        print(f"[Error] Connection failed: {e}")
    except Exception as e:
        print(f"[Error] {e}")

def logout_user() -> None:
    """Logout current user"""
    session = load_user_session()
    if session:
        username = session['user']['username']
        clear_user_session()
        print(f"[Success] Logged out {username}")
    else:
        print("[Info] No active session")

def whoami() -> None:
    """Show current logged in user"""
    session = load_user_session()
    if session:
        user = session['user']
        print(f"Logged in as: {user['username']}")
        print(f"User ID: {user['id']}")
        if 'email' in user:
            print(f"Email: {user.get('email')}")
    else:
        print("Not logged in")

def get_new_commit_id() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

def init_repo() -> None:
    if os.path.exists(folder_path):
        print("Repo is already initialized")
        return
    
    # Check if user is logged in
    session = load_user_session()
    if not session:
        print("[Error] You must be logged in to initialize a repo")
        print("Run 'forge login' or 'forge register' first")
        return
    
    os.mkdir(folder_path)

    json_files = ["files.json", "commits.json", "repo.json"]
    txt_files = ["current_commit.txt"]
    repo_name = Path.cwd().name
    folders = []

    try:
        for file in json_files:
            path = f"./{folder_path}/{file}"
            with open(path, "w") as f:
                f.write("[]")
        for file in txt_files:
            path = f"./{folder_path}/{file}"
            with open(path, "w") as f:
                f.write("")
        for folder in folders:
            path = f"./{folder_path}/{folder}"
            if os.path.exists(path) == False:
                os.mkdir(path)

        init_commit_id = get_new_commit_id()

        commits_data = [{"id": init_commit_id, "message": "Init commit.", "files": []}]
        
        with open(f"./{folder_path}/commits.json", "w") as f:
            f.write(json.dumps(commits_data))
        
        with open(f"./{folder_path}/current_commit.txt", "w") as f:
            f.write(init_commit_id)

        repo_data = {"name": repo_name}
        
        with open(f"./{folder_path}/repo.json", "w") as f:
            f.write(json.dumps(repo_data))

        print(f"[Local] Repository '{repo_name}' initialized successfully!")
        print(f"[Local] Use 'forge push' to create the repository on the server.")

    except Exception as e:
        print(f"Error occured: {e}")
        return

def get_repo_name() -> str:
    name = ""
    with open(f"./{folder_path}/repo.json", "r") as f:
        data = json.loads(f.read())
        name = data["name"]
    return name    

def load_file_data() -> list:
    data = []
    file_path = f"{folder_path}/files.json"

    try:
        with open(file_path, "r") as f:
            data = json.loads(f.read())
    except Exception as e:
        print(f"Error occured: {e}")
        return

    return data

def load_commit_data() -> list:
    data = []
    file_path = f"{folder_path}/commits.json"

    try:
        with open(file_path, "r") as f:
            data = json.loads(f.read())
    except Exception as e:
        print(f"Error occured: {e}")
        return

    return data

def add_file(file: dict) -> None:
    if not os.path.exists(folder_path):
        print("Init a repo first.")
        return

    files_entries = load_file_data()
    file_path = file.get("path")
    content = file.get("content")

    files_entries = [f for f in files_entries if f.get("file_path") != file_path]

    status = "new"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                existing_content = f.read()
            if existing_content != content:
                status = "modified"
        except:
            pass

    files_entries.append({
        "file_path": file_path,
        "file_content": content,
        "status": status
    })

    try:
        with open(f"{folder_path}/files.json", "w") as f:
            f.write(json.dumps(files_entries))
        
    except Exception as e:
        print(f"Error occured: {e}")

    
def remove_file(entry_file_path: str) -> None:
    if os.path.exists(folder_path) == False:
        print("Init a repo first.")
        return

    files_entries = load_file_data()
    file_path = f"{folder_path}/files.json"

    for i in files_entries:
        if i.get("file_path") == entry_file_path:
            try:
                index = files_entries.index(i)
                files_entries.pop(index)

                new_file_entry = {"file_path": i.get("file_path"), "file_content": i.get("file_content"), "status": "remove"}
                files_entries.append(new_file_entry)
            except:
                print("Error occured while removing previous file entry.")
                return

    try:
        with open(file_path, "w") as f:
            f.write(json.dumps(files_entries))
    except Exception as e:
        print(f"Error occured: {e}")
        return

def get_current_commit() -> str:
    if os.path.exists(folder_path) == False:
        print("Init a repo first.")
        return

    file_path = f"{folder_path}/current_commit.txt"
    current_commit_id = ""

    with open(file_path, "r") as f:
            current_commit_id = f.read()

    return current_commit_id

def add_commit_entry(commit: dict) -> None:
    commit_entries = load_commit_data()
    new_commit_entry = commit
    file_path = f"{folder_path}/commits.json"

    for commit_entry in commit_entries:
        if commit_entry.get("message") == commit.get("message"):
            print("Commit already exists.")
            return

    commit_entries.append(new_commit_entry)

    try:
        with open(file_path, "w") as f:
            f.write(json.dumps(commit_entries))
    except Exception as e:
        print(f"Error occured: {e}")
        return

def set_current_commit(commit_id: str) -> None:
    if os.path.exists(folder_path) == False:
        print("Init a repo first.")
        return

    file_path = f"{folder_path}/current_commit.txt"

    with open(file_path, "w") as f:
            f.write(commit_id)

def add_commit(message: str) -> None:
    if os.path.exists(folder_path) == False:
        print("Init a repo first.")
        return

    commit_id = get_new_commit_id()
    file_entries = load_file_data()

    add_commit_entry({"id": commit_id, "message": message, "files": file_entries})
    set_current_commit(commit_id)

def get_commit(commit_id: str) -> dict:
    commit_entries = load_commit_data()
    target_commit_entry = []

    for commit_entry in commit_entries:
        if commit_entry.get("id") == commit_id:
            target_commit_entry = commit_entry
        
    return target_commit_entry

def add_all() -> None:
    ignore_paths = [".forge"]
    if os.path.exists(".forgeignore"):
        with open(".forgeignore", "r") as f:
            ignore_paths += [line.strip() for line in f if line.strip()]

    current_commit = get_commit(get_current_commit())
    tracked_files = {f.get("file_path"): f for f in current_commit.get("files")}
    ignore_set = {Path(p).resolve() for p in ignore_paths}

    def ignored(p: Path) -> bool:
        p = p.resolve()
        return any(p.is_relative_to(x) for x in ignore_set)

    for root, dirs, files in os.walk("."):
        root_p = Path(root)

        dirs[:] = [d for d in dirs if not ignored(root_p / d)]

        existing_files = {os.path.join(root, f) for f in files}
        
        for file_path in list(tracked_files.keys()):
            if file_path not in existing_files and ".forge" not in file_path:
                remove_file(file_path)
                print("Removing missing file:", file_path)
                tracked_files.pop(file_path)

        for file in files:
            p = (root_p / file)
            if ignored(p) and p.name != ".forgeignore":
                continue

            try:
                with open(file_path, "r") as f:
                    content = f.read()
                add_file({"path": file_path, "content": content})
                print("Tracking file:", file_path)
            except Exception as e:
                print(f"Error reading file: {e}")

def checkout_commit(commit_id: str) -> None:
    commit = get_commit(commit_id)
    files = commit.get("files")

    try:
        for file in files:
            if file.get("status") == "add":
                with open(file.get("file_path"), "w") as f:
                    f.write(file.get("file_content"))
            elif file.get("status") == "new":
                with open(file.get("file_path"), "w") as f:
                    f.write(file.get("file_content"))
            elif file.get("status") == "remove":
                try:
                    os.remove(file.get("file_path"))
                except Exception as e:
                    print(f"Error removing file: {e}")
    except Exception as e:
        print(f"Error occured: {e}")
        return
    
def print_commit_data() -> None:
    commits = load_commit_data()
    for commit in commits:
        print(f"Commit ({commit.get('id')})")
        for file in commit.get("files"):
            print(f"File ({file.get('status')}): {file.get('file_path')}")
        print("\n")

def push_changes() -> None:
    headers = get_auth_headers()
    if not headers:
        print("[Error] Not logged in. Please run 'forge login' first.")
        return
    
    commit = get_commit(get_current_commit())
    repo_name = get_repo_name()
    
    # First, try to initialize repo on server if it doesn't exist
    commits_data = load_commit_data()
    files_data = load_file_data()
    
    init_data = {"name": repo_name, "commits": commits_data, "files": files_data}
    init_response = requests.post(f"{server_url}/api/repos/init", json=init_data, headers=headers)
    
    if init_response.status_code == 200:
        print(f"[Remote] Repository created on server")
    elif init_response.status_code == 400:
        # Repo already exists, that's fine
        print(f"[Remote] Using existing repository")
    else:
        print(f"[Error] Failed to initialize repo: {init_response.text}")
        return
    
    # Now push the current commit
    commit_data = {"id": commit.get("id"), "message": commit.get("message"), "files": commit.get("files"), "repo_name": repo_name}
    request = requests.post(f"{server_url}/api/repos/commits/add", json=commit_data, headers=headers)
    print(f"[Remote] (Commit Changes) {request.json()}")

    files_entries = load_file_data()

    reset_files_data = {"repo_name": repo_name}
    request = requests.post(f"{server_url}/api/repos/files/reset", json=reset_files_data, headers=headers)
    print(f"[Remote] (File Reset) {request.json()}")

    for file_entry in files_entries:
        file_data = {"path": file_entry.get("file_path"), "content": file_entry.get("file_content"), "repo_name": repo_name, "status": file_entry.get("status")}
        request = requests.post(f"{server_url}/api/repos/files/add", json=file_data, headers=headers)
        print(f"[Remote] (File Changes) {request.json()}")

    current_commit_data = {"repo_name": repo_name, "commit_id": get_current_commit()}
    request = requests.post(f"{server_url}/api/repos/commits/set_current", json=current_commit_data, headers=headers)
    print(f"[Remote] (Current Commit Changes) {request.json()}")

    push_data = {"repo_name": repo_name, "commit_id": commit.get("id")}
    request = requests.post(f"{server_url}/api/repos/push", json=push_data, headers=headers)
    
    print(f"[Remote] (Push Changes) {request.json()}")

    print(f"[Local] (Push Complete) Done")

def clone_repo(repo_full_name: str, dir_path: str = "") -> None:
    """
    Clone a repo using format: owner_id/repo_name
    Example: forge clone user123/myrepo
    """
    headers = get_auth_headers()
    
    # Parse owner/repo format
    if "/" in repo_full_name:
        owner_id, repo_name = repo_full_name.split("/", 1)
    else:
        print("[Error] Please specify repo in format: owner_id/repo_name")
        print("Example: forge clone user123/myrepo")
        return
    
    clone_data = {"repo_name": repo_name, "owner_id": owner_id}
    response = requests.post(f"{server_url}/api/repos/clone", json=clone_data, headers=headers)

    if response.status_code != 200:
        print(f"[Remote] Error: {response.json().get('detail', 'Repo not found')}")
        return

    data = response.json()
    if data.get("status") != "ok":
        print(f"[Remote] Error: {data.get('message', 'Repo not found')}")
        return

    print(f"[Remote] (Found Repo) {owner_id}/{repo_name}")
    if data.get("is_fork"):
        print(f"[Remote] (Fork) This is a fork of {data.get('forked_from')}")
    print(f"[Remote] (Starting Cloning) Starting...")

    files = data["files"]
    commits = data["commits"]
    current_commit = data["current_commit_id"]

    if dir_path == "":
        dir_path = repo_name

    try:
        os.mkdir(dir_path)
        os.mkdir(f"{dir_path}/.forge")
        repo_path = str(Path.cwd() / dir_path)

        with open(f"{dir_path}/.forge/files.json", "w") as f:
            f.write(json.dumps(files))
        
        with open(f"{dir_path}/.forge/commits.json", "w") as f:
            f.write(json.dumps(commits))

        with open(f"{dir_path}/.forge/current_commit.txt", "w") as f:
            f.write(current_commit)

        with open(f"{dir_path}/.forge/repo.json", "w") as f:
            repo_data = {
                "name": repo_name,
                "path": repo_path,
                "original_owner": owner_id,
                "cloned_from": f"{owner_id}/{repo_name}"
            }
            f.write(json.dumps(repo_data))

        for file in files:
            file_path = Path(f"{dir_path}") / file.get("file_path")

            file_path.parent.mkdir(parents=True, exist_ok=True)

            content = file.get("file_content") or ""
            file_path.write_text(content)

            print(f"[Remote] (Fetching File) {file.get('file_path')}...")

        print(f"[Local] (Completed Cloning) Completed...")
        print(f"[Local] cd {dir_path} to continue.")
        print(f"[Info] This is a clone of {owner_id}/{repo_name}")
        print(f"[Info] Push changes to create your own fork.")
    except Exception as e:
        print(f"Error occurred: {e}")

def fork_repo(repo_full_name: str) -> None:
    """
    Fork a repository to your account
    Format: owner_id/repo_name
    """
    headers = get_auth_headers()
    if not headers:
        print("[Error] Not logged in. Please run 'forge login' first.")
        return
    
    # Parse owner/repo format
    if "/" not in repo_full_name:
        print("[Error] Please specify repo in format: owner_id/repo_name")
        print("Example: forge fork user123/myrepo")
        return
    
    owner_id, repo_name = repo_full_name.split("/", 1)
    
    fork_data = {"repo_name": repo_name, "original_owner_id": owner_id}
    
    try:
        response = requests.post(
            f"{server_url}/api/repos/fork",
            json=fork_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            error = response.json().get("detail", "Fork failed")
            print(f"[Error] {error}")
            return
        
        data = response.json()
        if data.get("status") == "ok":
            fork_info = data.get("fork")
            print(f"[Success] Forked {repo_full_name} to your account!")
            print(f"[Success] Your fork: {fork_info['owner_id']}/{fork_info['name']}")
            print(f"[Info] Clone it with: forge clone {fork_info['owner_id']}/{fork_info['name']}")
        else:
            print("[Error] Fork failed")
    
    except Exception as e:
        print(f"[Error] {e}")

def delete_current_repo() -> None:
    """Delete the current repository"""
    headers = get_auth_headers()
    if not headers:
        print("[Error] Not logged in. Please run 'forge login' first.")
        return
    
    if not os.path.exists(folder_path):
        print("[Error] Not in a Forge repository")
        return
    
    repo_name = get_repo_name()
    
    print(f"⚠️  WARNING: You are about to delete '{repo_name}'")
    print("This action CANNOT be undone!")
    confirm = input("Type the repo name to confirm: ").strip()
    
    if confirm != repo_name:
        print("[Cancelled] Repo name doesn't match")
        return
    
    password = getpass.getpass("Enter your password to confirm: ")
    
    delete_data = {"repo_name": repo_name, "password": password}
    
    try:
        response = requests.delete(
            f"{server_url}/api/repos/delete",
            json=delete_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            error = response.json().get("detail", "Delete failed")
            print(f"[Error] {error}")
            return
        
        data = response.json()
        if data.get("status") == "ok":
            print(f"[Success] Repository '{repo_name}' deleted from server")
            print(f"[Info] Local files have NOT been deleted")
        else:
            print("[Error] Delete failed")
    
    except Exception as e:
        print(f"[Error] {e}")

def list_my_repos() -> None:
    """List all repos owned by the current user"""
    headers = get_auth_headers()
    if not headers:
        print("[Error] Not logged in. Please run 'forge login' first.")
        return
    
    try:
        response = requests.get(
            f"{server_url}/api/repos/list_mine",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print("[Error] Failed to fetch repos")
            return
        
        data = response.json()
        repos = data.get("repos", [])
        
        if not repos:
            print("No repositories found")
            print("Create one with 'forge init' and 'forge push'")
            return
        
        print(f"\n=== Your Repositories ({len(repos)}) ===\n")
        for repo in repos:
            print(f"📦 {repo['full_name']}")
            if repo.get("is_fork"):
                print(f"   └─ Fork of: {repo['forked_from']}")
            print()
    
    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use a valid command: init, login, register, logout, whoami, fork, delete, repos")
        quit()

    command = sys.argv[1]

    if command == "register":
        register_user()
    elif command == "login":
        login_user()
    elif command == "logout":
        logout_user()
    elif command == "whoami":
        whoami()
    elif command == "repos":
        list_my_repos()
    elif command == "fork":
        if len(sys.argv) < 3:
            print("Specify repo to fork: owner_id/repo_name")
            print("Example: forge fork user123/myrepo")
            quit()
        repo_full_name = sys.argv[2]
        fork_repo(repo_full_name)
    elif command == "delete":
        delete_current_repo()
    elif command == "init":
        init_repo()
    elif command == "add":
        if len(sys.argv) < 3:
            print("Add a file name.")
            quit()
        file_path = sys.argv[2]
        if file_path == ".":
            add_all()
        else:
            content = ""
            try:
                with open(f"./{file_path}", "r") as f:
                    content = f.read()
                
                add_file({"path": file_path, "content": content})
            except Exception as e:
                print(f"Error occured: {e}")
                quit()
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Add a file name.")
            quit()
        file_path = sys.argv[2]
        try:
            remove_file(file_path)
        except Exception as e:
            print(f"Error occured: {e}")
            quit()
    elif command == "commit":
        if len(sys.argv) < 3:
            print("Add a commit message.")
            quit()
        message = sys.argv[2]
        add_commit(message)
    elif command == "checkout":
        if len(sys.argv) < 3:
            print("Add a commit id.")
            quit()
        commit_id = sys.argv[2]
        if commit_id == "-":
            checkout_commit(get_current_commit())
        else:
            checkout_commit(commit_id)
    elif command == "list":
        if len(sys.argv) < 3:
            print("Add a thing to list eg: commits.")
            quit()
        list_id = sys.argv[2]
        if list_id == "commits":
            print_commit_data()
        else:
            print("Add a parameter to list eg: commits.")
            quit()
    elif command == "push":
        push_changes()
    elif command == "clone":
        if len(sys.argv) < 3:
            print("Add a repo to clone: owner_id/repo_name")
            print("Example: forge clone user123/myrepo")
            quit()
        repo_full_name = sys.argv[2]
        if len(sys.argv) >= 4:
            dir_path = sys.argv[3]
            clone_repo(repo_full_name, dir_path)
        else:
            clone_repo(repo_full_name)
    elif command == "help":
        print("\n=== Forge Commands ===\n")
        print("Authentication:")
        print("  register          - Create a new account")
        print("  login             - Login to your account")
        print("  logout            - Logout from your account")
        print("  whoami            - Show current user\n")
        print("Repository:")
        print("  init              - Initialize a new repo (local only)")
        print("  push              - Push changes to server (creates repo if needed)")
        print("  clone owner/repo  - Clone a repository")
        print("  fork owner/repo   - Fork a repository to your account")
        print("  delete            - Delete current repo from server")
        print("  repos             - List your repositories\n")
        print("Working with files:")
        print("  add <file|.>      - Add file(s) to staging")
        print("  remove <file>     - Remove file from repo")
        print("  commit <msg>      - Create a commit")
        print("  checkout <id|->   - Checkout a commit\n")
        print("Other:")
        print("  list commits      - Show commit history")
        print("  help              - Show this help message")
    else:
        print("Unknown command. Use 'forge help' to see available commands.")
        quit()