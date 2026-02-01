import sys
from forge.commands import auth, repo
from update import run_update
from pathlib import Path
from version import __version__

def main():
    if len(sys.argv) < 2:
        print("Use a valid command: init, login, register, logout, whoami, add, remove, commit, checkout, push, clone, help, update")
        return

    cmd = sys.argv[1]

    if cmd == "register":
        auth.register_user()
    elif cmd == "login":
        auth.login_user()
    elif cmd == "logout":
        auth.logout_user()
    elif cmd == "whoami":
        auth.whoami()
    elif cmd == "update":
            run_update()
    elif cmd == "init":
        repo.init_repo()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Add a file name.")
            return
        repo.add(sys.argv[2])
    elif cmd == "commit":
        if len(sys.argv) < 3:
            print("Add a commit message.")
            return
        repo.commit(sys.argv[2])
    elif cmd == "checkout":
        if len(sys.argv) < 3:
            print("Add a commit id.")
            return
        repo.checkout(sys.argv[2])
    elif cmd == "push":
        repo.push()
    elif cmd == "clone":
        if len(sys.argv) < 3:
            print("Add a repo to clone: owner_id/repo_name")
            return
        repo_full = sys.argv[2]
        dir_path = sys.argv[3] if len(sys.argv) >= 4 else ""
        repo.clone(repo_full, dir_path)
    elif cmd == "help":
        print("Commands: register, login, logout, whoami, init, add, commit, checkout, push, clone, update")
    elif cmd == "version":
        print(f"Version: {__version__}")
    else:
        print("Unknown command. Use 'help'.")

if __name__ == "__main__":
    main()
