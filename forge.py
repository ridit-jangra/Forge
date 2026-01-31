import os
import sys
import json
import datetime

folder_name = ".forge"
folder_path = f"./{folder_name}"

def get_new_commit_id() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

def init_repo() -> None:
    if os.path.exists(folder_path):
        print("Repo is already initialized")
        return
    
    os.mkdir(folder_path)

    json_files = ["files.json", "commits.json"]
    txt_files = ["current_commit.txt"]
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

        with open(f"./{folder_path}/commits.json", "w") as f:
            commits = [{"id": init_commit_id, "message": "Init commit.", "files": []}]
            f.write(json.dumps(commits))
        
        with open(f"./{folder_path}/current_commit.txt", "w") as f:
            f.write(init_commit_id)

    except Exception as e:
        print(f"Error occured: ${e}")
        return

    print("A new start!!!!")

def load_file_data() -> list:
    data = []
    file_path = f"{folder_path}/files.json"

    try:
        with open(file_path, "r") as f:
            data = json.loads(f.read())
    except Exception as e:
        print(f"Error occured: ${e}")
        return

    return data

def load_commit_data() -> list:
    data = []
    file_path = f"{folder_path}/commits.json"

    try:
        with open(file_path, "r") as f:
            data = json.loads(f.read())
    except Exception as e:
        print(f"Error occured: ${e}")
        return

    return data

def add_file(file: dict) -> None:
    if os.path.exists(folder_path) == False:
        print("Init a repo first.")
        return

    file_entry = {"file_path": file.get("path"), "file_content": file.get("content"), "status": "new"}
    files_entries = load_file_data()
    file_path = f"{folder_path}/files.json"

    for i in files_entries:
        if (
            i.get("file_path") == file.get("path")
        ):
            try:
                index = files_entries.index(i)
                files_entries.pop(index)
                content = ""
                with open(i.get("file_path"), "w") as f:
                    content = f.read()

                new_file_entry = {"file_path": i.get("file_path"), "file_content": content, "status": "modified"}
                files_entries.append(new_file_entry)
            except:
                print("Error occured while removing previous file entry.")
                return
        

    files_entries.append(file_entry)

    try:
        with open(file_path, "w") as f:
            f.write(json.dumps(files_entries))
    except Exception as e:
        print(f"Error occured: ${e}")
        return
    
def remove_file(entry_file_path: str) -> None:
    if os.path.exists(folder_path) == False:
        print("Init a repo first.")
        return

    files_entries = load_file_data()
    file_path = f"{folder_path}/files.json"

    for i in files_entries:
        if i.get("file_path") == entry_file_path:
            print("removing", i.get("file_path"))
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
        print(f"Error occured: ${e}")
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
        print(f"Error occured: ${e}")
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
                    print(f"Error removing file: ${e}")
    except Exception as e:
        print(f"Error occured: {e}")
        return
    
def print_commit_data() -> None:
    commits = load_commit_data()
    for commit in commits:
        print(f"Commit ({commit.get("id")})")
        for file in commit.get("files"):
            print(f"File ({file.get("status")}): {file.get("file_path")}")
        print("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use a valid command: init")
        quit()

    command = sys.argv[1]

    if command == "init":
        init_repo()
    elif command == "add":
        if len(sys.argv) < 3:
            print("Add a file name.")
            quit()
        file_path = sys.argv[2]
        content = ""
        try:
            with open(f"./{file_path}", "r") as f:
                content = f.read()
            
            add_file({"path": file_path, "content": content})
        except Exception as e:
            print(f"Error occured: ${e}")
            quit()
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Add a file name.")
            quit()
        file_path = sys.argv[2]
        try:
            remove_file(file_path)
        except Exception as e:
            print(f"Error occured: ${e}")
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
        checkout_commit(commit_id)
    elif command == "list":
        if len(sys.argv) < 3:
            print("Add a thing to list eg: commits.")
            quit()
        list_id = sys.argv[2]
        if list_id == "commits":
            print_commit_data()
        else:
            print("Add a thing to list eg: commits.")
            quit()
    elif command == "help":
        print("All commands: init, list, add, remove")
    else:
        print("Use a valid command: init, list, add, remove")
        quit()