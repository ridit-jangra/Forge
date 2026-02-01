# Forge

**Forge** is a lightweight, Git-like version control system built in Python with a custom remote server.  
It allows you to track files, commit changes, push to a remote repository, clone repos, and manage versions using a simple CLI.

---

## Features

### Local Version Control
- Initialize a repository (`init`)
- Track files individually or all at once (`add`)
- Remove files from tracking (`remove`)
- Commit changes with messages (`commit`)
- Checkout previous commits (`checkout`)
- List commit history (`list commits`)
- `.forgeignore` support for ignoring files and folders

### Remote Features
- User authentication (`register`, `login`, `logout`)
- Push repositories to a Forge server (`push`)
- Clone remote repositories (`clone`)
- Fork repositories (`fork`)
- List your repositories (`repos`)
- Delete repositories (`delete`)

---

## Installation

### Option 1: Python (Development)

```bash
git clone https://github.com/ridit-jangra/Forge
cd Forge
pip install -r requirements.txt
python forge.py <command>
```

---

### Option 2: Executable (Recommended)

```bash
forge.exe <command>
```

No Python installation required.

---

## Configuration

Optional `.env` file:

```env
FORGE_SERVER_URL=http://localhost:8000
FORGE_SESSION=.forge_session
```

---

## Usage

```bash
forge init
forge add .
forge commit "Initial commit"
forge push
```

---

## Limitations
- Text files only
- No branches or merges
- Linear history
- Early-stage project

---

## License
MIT License
