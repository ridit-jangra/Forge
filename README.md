# Forge

**Forge** is a lightweight, Git-like version control system built in Python. It allows you to track files, commit changes, remove files, and checkout previous commits using a simple CLI.

---

## Features

- Initialize a repository (`init`)
- Track files individually or all at once (`add`)
- Remove files from tracking (`remove`)
- Commit changes with messages (`commit`)
- Checkout previous commits (`checkout`)
- List all commits (`list commits`)
- Supports `.forgeignore` for ignoring files/folders

---

## Installation

1. Clone or download the repository:

```bash
git clone <repo-url>
cd Forge
```

2. Make sure **Python 3** is installed.

3. Run commands using:

```bash
python forge.py <command>
```

---

## Usage

### Initialize Repository

```bash
python forge.py init
```

Creates a `.forge` folder with initial commit and tracking files.

---

### Track Files

Track a single file:

```bash
python forge.py add filename
```

Track all files in the project folder (ignores `.forge` and `.forgeignore`):

```bash
python forge.py add .
```

---

### Remove a File

```bash
python forge.py remove filename
```

Marks the file as removed in the current commit.

---

### Commit Changes

```bash
python forge.py commit "Commit message"
```

Stores the current state of tracked files with a unique commit ID.

---

### Checkout a Commit

```bash
python forge.py checkout <commit_id>
```

Reverts the project to the state of the specified commit.

---

### List Commits

```bash
python forge.py list commits
```

Displays all commits and tracked files with their status (`new`, `modified`, `remove`).

---

### Help

```bash
python forge.py help
```

Shows all available commands.

---

## `.forgeignore`

You can ignore files or folders from tracking by creating a `.forgeignore` file in the root of your project. Each line should contain a file or folder path to ignore.

Example:

```
node_modules
*.log
.env
```

---

## Example Workflow

```bash
python forge.py init
python forge.py add .
python forge.py commit "Initial commit"
python forge.py add some_file.py
python forge.py commit "Added some_file"
python forge.py list commits
python forge.py checkout <commit_id>
```

---

## License

MIT License
